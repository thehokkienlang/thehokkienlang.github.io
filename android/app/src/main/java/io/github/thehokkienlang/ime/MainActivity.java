package io.github.thehokkienlang.ime;

import android.app.Activity;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.provider.Settings;
import android.view.ViewGroup;
import android.view.inputmethod.InputMethodManager;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;

/** Setup screen: turn the keyboard on, switch to it, and try it. */
public class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        int pad = Math.round(20 * getResources().getDisplayMetrics().density);

        LinearLayout column = new LinearLayout(this);
        column.setOrientation(LinearLayout.VERTICAL);
        column.setPadding(pad, pad, pad, pad);

        TextView intro = new TextView(this);
        intro.setText(R.string.setup_intro);
        intro.setTextSize(16);
        intro.setPadding(0, 0, 0, pad);
        column.addView(intro, matchWidth());

        Button enable = new Button(this);
        enable.setText(R.string.setup_enable);
        enable.setAllCaps(false);
        enable.setOnClickListener(view -> startActivity(new Intent(Settings.ACTION_INPUT_METHOD_SETTINGS)));
        column.addView(enable, matchWidth());

        Button choose = new Button(this);
        choose.setText(R.string.setup_choose);
        choose.setAllCaps(false);
        choose.setOnClickListener(view -> {
            InputMethodManager manager = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
            if (manager != null) manager.showInputMethodPicker();
        });
        column.addView(choose, matchWidth());

        EditText trial = new EditText(this);
        trial.setHint(R.string.setup_try);
        trial.setMinLines(3);
        trial.setTextSize(20);
        LinearLayout.LayoutParams trialParams = matchWidth();
        trialParams.topMargin = pad;
        column.addView(trial, trialParams);

        ScrollView scroll = new ScrollView(this);
        scroll.addView(column);
        setContentView(scroll);
    }

    private static LinearLayout.LayoutParams matchWidth() {
        return new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
    }
}
