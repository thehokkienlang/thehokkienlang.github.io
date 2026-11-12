package io.github.thehokkienlang.ime;

import android.annotation.SuppressLint;
import android.content.Context;
import android.content.res.Configuration;
import android.inputmethodservice.InputMethodService;
import android.net.Uri;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.view.KeyEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputConnection;
import android.view.inputmethod.InputMethodManager;
import android.webkit.JavascriptInterface;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.Locale;

/**
 * The TLI system keyboard. The keys, candidates and composition logic are the website's own
 * IME code (assets copied at build time), shown in a WebView; this class passes its output to
 * the focused app.
 */
public class TliKeyboardService extends InputMethodService {
    // A local-only origin: every request is answered from the APK's assets, never the network.
    private static final String HOST = "appassets.androidplatform.net";
    private static final String PAGE = "https://" + HOST + "/keyboard/index.html";
    private static final int HEIGHT_PORTRAIT_DP = 306;
    private static final int HEIGHT_LANDSCAPE_DP = 214;

    private final Handler main = new Handler(Looper.getMainLooper());
    private WebView keyboard;
    private boolean pageReady;
    private boolean composing;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    public View onCreateInputView() {
        if (keyboard == null) {
            keyboard = new WebView(this);
            WebSettings settings = keyboard.getSettings();
            settings.setJavaScriptEnabled(true);
            settings.setDomStorageEnabled(true); // learned candidate preferences
            settings.setAllowFileAccess(false);
            settings.setAllowContentAccess(false);
            settings.setTextZoom(100);
            keyboard.setBackgroundColor(0xFFE4EAEC);
            keyboard.setOverScrollMode(View.OVER_SCROLL_NEVER);
            keyboard.setVerticalScrollBarEnabled(false);
            keyboard.setHorizontalScrollBarEnabled(false);
            keyboard.setHapticFeedbackEnabled(false);
            keyboard.setWebViewClient(new AssetClient());
            keyboard.addJavascriptInterface(new Bridge(), "TliHost");
            keyboard.loadUrl(PAGE);
        }
        ViewGroup parent = (ViewGroup) keyboard.getParent();
        if (parent != null) parent.removeView(keyboard);
        applyHeight();
        return keyboard;
    }

    private void applyHeight() {
        boolean landscape = getResources().getConfiguration().orientation == Configuration.ORIENTATION_LANDSCAPE;
        float density = getResources().getDisplayMetrics().density;
        int height = Math.round((landscape ? HEIGHT_LANDSCAPE_DP : HEIGHT_PORTRAIT_DP) * density);
        keyboard.setLayoutParams(new ViewGroup.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, height));
    }

    @Override
    public boolean onEvaluateFullscreenMode() {
        return false; // keep the app visible in landscape
    }

    @Override
    public void onStartInputView(EditorInfo info, boolean restarting) {
        super.onStartInputView(info, restarting);
        resetPage();
    }

    @Override
    public void onFinishInputView(boolean finishingInput) {
        super.onFinishInputView(finishingInput);
        resetPage();
    }

    @Override
    public void onUpdateSelection(int oldSelStart, int oldSelEnd, int newSelStart, int newSelEnd,
                                  int candidatesStart, int candidatesEnd) {
        super.onUpdateSelection(oldSelStart, oldSelEnd, newSelStart, newSelEnd, candidatesStart, candidatesEnd);
        if (!composing) return;
        boolean ended = candidatesStart < 0;
        boolean movedAway = !ended && (newSelStart != newSelEnd || newSelEnd != candidatesEnd);
        if (ended || movedAway) {
            // The user moved the cursor or the app ended the composition: keep the text, start afresh.
            InputConnection connection = getCurrentInputConnection();
            if (movedAway && connection != null) connection.finishComposingText();
            resetPage();
        }
    }

    @Override
    public void onDestroy() {
        if (keyboard != null) {
            keyboard.destroy();
            keyboard = null;
        }
        super.onDestroy();
    }

    private void resetPage() {
        composing = false;
        if (keyboard != null && pageReady) {
            keyboard.evaluateJavascript("window.TliKeyboard && window.TliKeyboard.reset()", null);
        }
    }

    /** Serves the page from the APK's assets, laid out like the website's root. */
    private final class AssetClient extends WebViewClient {
        @Override
        public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
            Uri uri = request.getUrl();
            String path = uri.getPath();
            if (HOST.equals(uri.getHost()) && path != null && path.length() > 1 && !path.contains("..")) {
                try {
                    return new WebResourceResponse(mimeType(path), encoding(path), getAssets().open(path.substring(1)));
                } catch (IOException missing) {
                    // fall through to the empty response
                }
            }
            return new WebResourceResponse("text/plain", "utf-8", 404, "Not found", null,
                    new ByteArrayInputStream(new byte[0]));
        }

        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            return true; // the keyboard page never navigates
        }

        @Override
        public void onPageFinished(WebView view, String url) {
            pageReady = true;
        }
    }

    private static String mimeType(String path) {
        String name = path.toLowerCase(Locale.ROOT);
        if (name.endsWith(".html")) return "text/html";
        if (name.endsWith(".js")) return "text/javascript";
        if (name.endsWith(".css")) return "text/css";
        if (name.endsWith(".json")) return "application/json";
        if (name.endsWith(".woff2")) return "font/woff2";
        if (name.endsWith(".png")) return "image/png";
        if (name.endsWith(".svg")) return "image/svg+xml";
        return "application/octet-stream";
    }

    private static String encoding(String path) {
        String name = path.toLowerCase(Locale.ROOT);
        return name.endsWith(".woff2") || name.endsWith(".png") ? null : "utf-8";
    }

    /** Called by keyboard.js. WebView calls these off the main thread. */
    private final class Bridge {
        @JavascriptInterface
        public void setComposing(final String text) {
            main.post(() -> {
                InputConnection connection = getCurrentInputConnection();
                if (connection == null) return;
                if (text.isEmpty()) {
                    connection.commitText("", 1);
                    composing = false;
                } else {
                    connection.setComposingText(text, 1);
                    composing = true;
                }
            });
        }

        @JavascriptInterface
        public void commit(final String text) {
            main.post(() -> {
                InputConnection connection = getCurrentInputConnection();
                if (connection == null) return;
                composing = false;
                connection.commitText(text, 1);
            });
        }

        @JavascriptInterface
        public void deleteBackward() {
            main.post(() -> sendDownUpKeyEvents(KeyEvent.KEYCODE_DEL));
        }

        @JavascriptInterface
        public void enter() {
            main.post(() -> {
                InputConnection connection = getCurrentInputConnection();
                EditorInfo info = getCurrentInputEditorInfo();
                if (connection == null) return;
                int action = info == null ? EditorInfo.IME_ACTION_NONE : info.imeOptions & EditorInfo.IME_MASK_ACTION;
                boolean plainEnter = info == null
                        || (info.imeOptions & EditorInfo.IME_FLAG_NO_ENTER_ACTION) != 0
                        || action == EditorInfo.IME_ACTION_NONE
                        || action == EditorInfo.IME_ACTION_UNSPECIFIED;
                if (plainEnter) sendDownUpKeyEvents(KeyEvent.KEYCODE_ENTER);
                else connection.performEditorAction(action);
            });
        }

        @JavascriptInterface
        public void switchKeyboard() {
            main.post(() -> {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P && switchToNextInputMethod(false)) return;
                InputMethodManager manager = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
                if (manager != null) manager.showInputMethodPicker();
            });
        }
    }
}
