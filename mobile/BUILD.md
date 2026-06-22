# Building & Distributing the Infreight Rates App

The app is built and shipped with [EAS](https://docs.expo.dev/eas/) (Expo
Application Services). Profiles live in `eas.json`.

## One-time setup

```bash
npm install -g eas-cli      # the EAS CLI (global, not a project dep)
eas login                   # sign in to your Expo account
eas init                    # links this project + writes extra.eas.projectId
```

`eas init` is what populates the Expo **project ID** in `app.json` — it is
intentionally not committed here.

Set the backend the build should talk to (baked in at build time):

```bash
# .env or EAS env var
EXPO_PUBLIC_API_URL=https://<your-railway-backend>
```

For production builds, store this as an EAS environment variable instead:
`eas env:create --name EXPO_PUBLIC_API_URL --value https://... --environment production`

## Identifiers

- iOS bundle identifier: `com.infreight.rates`
- Android package: `com.infreight.rates`

(Change both in `app.json` if you want a different namespace — do it before the
first build, since stores tie listings to these.)

## Build profiles (`eas.json`)

| Profile | What it produces | Use |
|---|---|---|
| `development` | Dev client (internal). iOS simulator build enabled. | Local debugging with `expo-dev-client` (run `npx expo install expo-dev-client` first). |
| `preview` | Internal install — Android `.apk`, iOS ad-hoc/TestFlight | Hand a build to internal testers. |
| `production` | Store-ready (auto-incrementing build number) | TestFlight / App Store / Play. |

## Common commands

```bash
# Quick test on a real phone WITHOUT any build (Expo Go):
npx expo start            # scan the QR

# Internal builds:
eas build --profile preview --platform android   # .apk to sideload
eas build --profile preview --platform ios       # needs an Apple Developer account

# Production + submit:
eas build --profile production --platform all
eas submit --profile production --platform ios    # -> TestFlight / App Store
eas submit --profile production --platform android # -> Play Console
```

## iOS note

Any iOS install — even internal TestFlight — requires an **Apple Developer
account** ($99/yr). There is no "just a link" install path on iOS. Android can
install the `preview` `.apk` directly with no account.

## Credentials

Signing credentials (iOS certs/profiles, Android keystore) are managed by EAS
(`eas credentials`) and stored on Expo's servers — none are committed to this
repo.
