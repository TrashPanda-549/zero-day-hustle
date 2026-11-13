# Zero Day Hustle

A trading game set in the hacker underground. You have 30 days, $2,000 and a debt to the Syndicate that grows every day. Buy low, sell high, and stay off the radar.

![App icon](assets/logo.png)

## Play in the browser (and on iPhone)

**https://trashpanda-549.github.io/zero-day-hustle/**

It runs on any phone or computer. On an iPhone or iPad, open the link in Safari, tap Share, then **Add to Home Screen**: it then opens full screen like an app and keeps working offline.

## Download

Grab the latest build from the [Releases page](../../releases):

| Platform | File | Notes |
| --- | --- | --- |
| Windows | `ZeroDayHustle-<version>-windows.exe` | Portable, no install. SmartScreen may warn because the app is unsigned: choose More info, then Run anyway. |
| Android | `ZeroDayHustle-<version>-android.apk` | Android 7 or newer. Allow "install unknown apps" when asked. |
| Mac | `ZeroDayHustle-<version>-mac.dmg` | Unsigned: right-click the app and choose Open the first time. |
| iPhone | `ZeroDayHustle-<version>-ios-unsigned.ipa` | Unsigned, so it only installs through a sideloading tool that signs it with your own Apple ID. For most people the browser version above is the easier way. |

## How to play

- Ten goods, from Warez up to Zero-Days, with prices that change every day. News events make some scarce and others dirt cheap.
- Tunnel between eight locations. Every trip takes a day.
- The Hackerspace is home: pay down or borrow from the Syndicate broker, and park cash in the cold wallet where it earns interest and can't be phished.
- Big deals raise your Heat, and Heat brings traces. Run, counter-hack through your proxies, or wipe your drive to escape.
- If your OpSec hits zero you are busted and the run scores nothing. Laying low for a day cools things off.
- Only cash and your cold wallet count at the end, minus whatever you still owe.

## Terminal version

There is also a text-only version that needs nothing but Python 3:

```
python hustle.py
```

## Building from source

The game is a single page, `www/index.html`, which also runs in any browser. The desktop apps wrap it with Electron and the Android app with Capacitor.

```
npm install
npm start            # run the desktop app
npm run dist:win     # build the Windows .exe into dist/
npm run dist:mac     # build the Mac .dmg (on a Mac)
```

For Android, with Java 21 and the Android SDK installed:

```
npx cap add android
npx cap sync android
cd android && ./gradlew assembleDebug
```