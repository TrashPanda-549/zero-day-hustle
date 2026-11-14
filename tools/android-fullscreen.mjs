// Makes the generated Android app stay full screen.
//
// Hiding the system bars on launch is done in capacitor.config.json
// (plugins.SystemBars.hidden). The one thing that has no config option is *how*
// the bars come back: Android's default is that a swipe from the edge brings
// them back and leaves them there, which would letterbox the game for the rest
// of the session. This inserts the two lines that ask for the transient
// ("sticky immersive") behaviour instead, so a swipe shows the bars for a
// moment and they hide themselves again.
//
// android/ is generated and gitignored, so this runs after `npx cap sync android`:
//
//     npx cap add android && npx cap sync android && node tools/android-fullscreen.mjs
//
// It is deliberately picky: if MainActivity.java is not the empty class Capacitor
// generates, it fails loudly rather than guessing.

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { resolve } from 'node:path';

const root = resolve(process.argv[2] ?? '.');
const { appId } = JSON.parse(readFileSync(resolve(root, 'capacitor.config.json'), 'utf8'));
const relative = `android/app/src/main/java/${appId.split('.').join('/')}/MainActivity.java`;
const file = resolve(root, relative);

if (!existsSync(file)) {
  console.error(`android-fullscreen: ${relative} does not exist. Run \`npx cap add android\` and \`npx cap sync android\` first.`);
  process.exit(1);
}

const source = readFileSync(file, 'utf8');

if (source.includes('BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE')) {
  console.log(`android-fullscreen: ${relative} is already patched, nothing to do.`);
  process.exit(0);
}

// The file Capacitor generates is exactly:
//
//   package <appId>;
//
//   import com.getcapacitor.BridgeActivity;
//
//   public class MainActivity extends BridgeActivity {}
const emptyClass = /public class MainActivity extends BridgeActivity \{\s*\}/;
const importLine = 'import com.getcapacitor.BridgeActivity;';

if (!emptyClass.test(source) || !source.includes(importLine)) {
  console.error(
    `android-fullscreen: ${relative} is not the empty class Capacitor generates, so the full-screen patch was not applied.\n` +
      `Capacitor's template has changed; update tools/android-fullscreen.mjs.\n--- the file ---\n${source}`
  );
  process.exit(1);
}

const body = `
    // Keep the game full screen: show the system bars only while they are being
    // used, then hide them again. The bars are hidden on launch by
    // plugins.SystemBars.hidden in capacitor.config.json; this is the behaviour
    // Capacitor has no config option for. Inserted by tools/android-fullscreen.mjs.
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        WindowCompat.getInsetsController(getWindow(), getWindow().getDecorView()).setSystemBarsBehavior(
            WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        );
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            WindowCompat.getInsetsController(getWindow(), getWindow().getDecorView()).hide(WindowInsetsCompat.Type.systemBars());
        }
    }
`;

const patched = source
  .replace(
    importLine,
    [
      'import android.os.Bundle;',
      'import androidx.core.view.WindowCompat;',
      'import androidx.core.view.WindowInsetsCompat;',
      'import androidx.core.view.WindowInsetsControllerCompat;',
      importLine,
    ].join('\n')
  )
  .replace(emptyClass, `public class MainActivity extends BridgeActivity {\n${body}}`);

writeFileSync(file, patched);
console.log(`android-fullscreen: patched ${relative} for transient system bars.`);
