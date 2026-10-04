"""Static ranking has no source-row state and never mutates lexical records."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from tools.dictionary_ranking import PRIORITY_COLUMNS, canonical_key, load_priority, rank_entries, segment_match, annotate_entries
from tools.dictionary_schema import make_entry_id

ROOT = Path(__file__).resolve().parents[1]


def record(word, reading):
    return dict(hanri=word,reading=reading,corrected='',entry_type='lexical',entry_id=make_entry_id(word,0))


class StaticRankingTests(unittest.TestCase):
    def setUp(self):
        self.entries = [record(w,'가') for w in ('加','家','架','迦')]
        self.entries.sort(key=canonical_key)

    def test_row_independence(self):
        expected=[e['entry_id'] for e in rank_entries(self.entries,'가')]
        changed=[{**e,'row':i+99} for i,e in enumerate(reversed(self.entries))]
        self.assertEqual(expected,[e['entry_id'] for e in rank_entries(changed,'가')])

    def test_partial_rank_one_and_middle(self):
        a,b,c,d=self.entries
        for chosen,rank,expected in ((c,1,[c,a,b,d]),(d,2,[a,d,b,c])):
            self.assertEqual(rank_entries(self.entries,'가',{'가':{chosen['entry_id']:rank}}),expected)
        self.assertEqual(rank_entries(self.entries,'나',{'가':{c['entry_id']:1}}),self.entries)

    def priority_file(self, rows):
        directory=tempfile.TemporaryDirectory(); self.addCleanup(directory.cleanup)
        path=Path(directory.name)/'dictionary_priority.tsv'
        with path.open('w',encoding='utf-8',newline='') as stream:
            writer=csv.writer(stream,delimiter='\t',lineterminator='\r\n'); writer.writerow(PRIORITY_COLUMNS);writer.writerows(rows)
        return path

    def test_validation_conflicts_range_label_eligibility_and_identity(self):
        a,b,*_=self.entries
        base=['가',a['hanri'],a['entry_id'],'1']
        invalid=[
            [base,['가',b['hanri'],b['entry_id'],'1']],
            [base,base],
            [['가',a['hanri'],a['entry_id'],'5']],
            [['가','stale',a['entry_id'],'1']],
            [['나',a['hanri'],a['entry_id'],'1']],
            [['가',a['hanri'],a['entry_id']+'-sandhi','1']],
            [['가',a['hanri'],a['entry_id'],'0']],
        ]
        for rows in invalid:
            with self.subTest(rows=rows),self.assertRaises(ValueError): load_priority(self.priority_file(rows),self.entries)

    def test_noncontiguous_contextual_ranks(self):
        a,b,c,d=self.entries
        rows=[['가',c['hanri'],c['entry_id'],'1'],['가',d['hanri'],d['entry_id'],'3'],[c['hanri'],c['hanri'],c['entry_id'],'1']]
        overrides=load_priority(self.priority_file(rows),self.entries)
        self.assertEqual(rank_entries(self.entries,'가',overrides),[c,a,d,b])
        self.assertIn(c['hanri'],overrides)
        different=load_priority(self.priority_file([
            ['가',c['hanri'],c['entry_id'],'2'],
            [c['hanri'],c['hanri'],c['entry_id'],'1'],
        ]),self.entries)
        self.assertEqual(rank_entries(self.entries,'가',different),[a,c,b,d])
        self.assertEqual(different[c['hanri']][c['entry_id']],1)

    def test_validation_schema_and_normalized_keys(self):
        a=self.entries[0]
        for row in (
            ['',a['hanri'],a['entry_id'],'1'],
            ['가',a['hanri'],a['entry_id'],'1'],
            ['가 ',a['hanri'],a['entry_id'],'1'],
            ['〃',a['hanri'],a['entry_id'],'1'],
            ['가',a['hanri'],a['entry_id']],
            ['가',a['hanri'],a['entry_id'],'1','extra'],
        ):
            with self.subTest(row=row),self.assertRaises(ValueError):
                load_priority(self.priority_file([row]),self.entries)
        path=self.priority_file([])
        path.write_text('key\tentry\tentry_id\trank\r\n',encoding='utf-8',newline='')
        with self.assertRaises(ValueError): load_priority(path,self.entries)

    def test_generated_variants_keep_source_precedence(self):
        a,b,*_=self.entries
        generated={**a,'entry_id':a['entry_id']+'-sandhi','raw':a,'auto_sandhi':True}
        result=rank_entries([generated,b,a],'가',{'가':{a['entry_id']:1}})
        self.assertLess(result.index(a),result.index(generated))

    def test_obsolete_override_cleanup_keeps_hanri_and_distinct_homophones(self):
        import csv
        with (ROOT/'data/hokkien_hanri_dict.tsv').open(encoding='utf-8',newline='') as stream:
            entries={r['entry_id']:r for r in csv.DictReader(stream,delimiter='\t') if r['entry_id']}
        report=json.loads((ROOT/'docs/hangul-override-cleanup.json').read_text(encoding='utf-8'))
        for pair in report['removedOverrides']:
            self.assertNotIn(pair['old']['entry_id'],entries)
            retained=entries[pair['retained']['entry_id']]
            self.assertEqual(retained['reading'],pair['old']['reading'])
            self.assertEqual(retained['entry_type'],'lexical')
        self.assertNotIn('U+C2DC_00',entries)
        self.assertEqual((entries['U+662F_00']['hanri'],entries['U+662F_00']['reading']),('是','시5'))
        for identity in ('U+AC10_00','U+BF94_00','U+C560_00','U+D5C8_00'):
            self.assertEqual(entries[identity]['entry_type'],'hangul_override')

    def test_polyphonic_and_segmentation_defaults(self):
        data=json.loads((ROOT/'public/data/hokkien-hanri-dict.json').read_text(encoding='utf-8'))
        entries=[e for e in data['entries'] if e.get('active') and not e.get('autoSandhi') and e['kind']=='plain_hanri']
        defaults=json.loads((ROOT/'tests/fixtures/static-reading-defaults.json').read_text(encoding='utf-8'))
        for expected in defaults['defaults']:
            if expected['key'] and all('\u3400'<=c<='\u9fff' or ord(c)>0x20000 for c in expected['key']):
                found=segment_match(expected['key'],0,entries)
                self.assertEqual((found['hanri'],found['reading']) if found else (None,None),(expected['hanri'],expected['reading']),expected['key'])


if __name__=='__main__': unittest.main()
