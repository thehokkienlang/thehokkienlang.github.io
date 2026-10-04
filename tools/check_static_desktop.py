"""Check real Python readers, contextual defaults and physical TSV reordering."""
import csv
import json
import os
import shutil
import tempfile
from pathlib import Path

from build_dictionary_json import REPO_ROOT, load_ime_module, load_tone_marker_module


def main():
    os.environ['HOKKIEN_GITHUB_REPO_PATH']=str(REPO_ROOT)
    os.environ['HOKKIEN_HANRI_DICT_PATH']=str(REPO_ROOT/'data/hokkien_hanri_dict.tsv')
    pad=load_ime_module()
    converter=load_tone_marker_module()
    assert len(pad.HANRI_DICT)>2000,pad.HANRI_DICT_SOURCE
    expected=json.loads((REPO_ROOT/'tests/fixtures/static-reading-defaults.json').read_text(encoding='utf-8'))
    count=0
    for item in expected['defaults']:
        text=item['key']
        if not pad.field_is_plain_hanri_key(text):
            continue
        match=pad.static_audio_hanri_match(text,0)
        html=converter.tsv_hanri_segment_for_run(text,0)
        desired=(item['hanri'],item['reading']) if item['id'] else None
        assert match==desired,(text,'audio',match,desired)
        assert html==desired,(text,'HTML',html,desired)
        count+=1
    for item in expected['desktopMixedDefaults']:
        text=item['key']
        match=next(((key,reading) for key,reading in pad.MIXED_AUDIO_HANRI_INDEX if text.startswith(key)),None)
        html=converter.mixed_tsv_hanri_match(text,0)
        assert match==(tuple(item['audio']) if item['audio'] else None),(text,'mixed audio',match,item['audio'])
        assert html==(tuple(item['html']) if item['html'] else None),(text,'mixed HTML',html,item['html'])
    audio_defaults={}
    for key,reading in pad.AUDIO_READING_INDEX:
        audio_defaults.setdefault(key,reading)
    assert audio_defaults==expected['desktopAudioReadingDefaults'],'Hangul audio default changed from pre-reform snapshot'
    source=REPO_ROOT/'data/hokkien_hanri_dict.tsv'
    with source.open(encoding='utf-8',newline='') as stream:
        rows=list(csv.reader(stream,delimiter='\t'))
    with tempfile.TemporaryDirectory() as folder:
        copied=Path(folder)/source.name
        with copied.open('w',encoding='utf-8',newline='') as stream:
            writer=csv.writer(stream,delimiter='\t',lineterminator='\r\n')
            writer.writerow(rows[0]); writer.writerows(reversed(rows[1:]))
        for name in ('dictionary_priority.tsv','dictionary_entry_id_registry.tsv'):
            shutil.copyfile(source.with_name(name),copied.with_name(name))
        reordered=pad.load_hanri_dict(copied)
        identity=lambda groups:{key:[e['entry_id'] for e in values] for key,values in groups.items()}
        assert identity(reordered)==identity(pad.HANRI_DICT),'Source-row-dependent Python candidate order'
        assert list(reordered)==list(pad.HANRI_DICT),'Source-row-dependent reading-group traversal'
        exact,base=pad.build_hanri_candidate_tests(reordered)
        assert [(typed,key) for typed,key,_ in exact]==[(typed,key) for typed,key,_ in pad.HANRI_EXACT_CANDIDATE_TESTS]
        assert [key for key,_ in base]==[key for key,_ in pad.HANRI_BASE_CANDIDATE_TESTS]
        assert pad.build_audio_hanri_index(reordered)==pad.AUDIO_HANRI_INDEX,'Source-row-dependent audio defaults'
        assert pad.build_audio_reading_index(reordered)==pad.AUDIO_READING_INDEX,'Source-row-dependent Hangul audio defaults'
        records=pad.build_audio_hanri_segment_index(reordered)
        for item in expected['defaults']:
            if pad.field_is_plain_hanri_key(item['key']):
                actual=pad.dictionary_ranking_api().segment_match(item['key'],0,records)
                assert ((actual['hanri'],pad.entry_audio_reading(actual)) if actual else None)==((item['hanri'],item['reading']) if item['id'] else None)
    print(f'PASS: Python audio/HTML defaults match {count} Web contexts; {len(expected["desktopMixedDefaults"])} mixed contexts retain their platform baseline; reversed TSV preserves every Local candidate and audio default.')


if __name__=='__main__': main()
