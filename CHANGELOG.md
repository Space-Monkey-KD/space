    - Default volume
- Different audio output devices for speech and media can be specified.
- Support for Arch Linux.

### Changed
- Improved directory structure.
- Paths improvements for better _platform-independency_ and UX.
    - Use system temporary directory for recordings/answers, which is usually in RAM to avoid using system storage.
    - Default install path is now _/opt/spacePi_.
- Uses pocketsphinx only from PyPI (not the extra `git pull` anymore), which saves about 200 MB on bandwidth and 250 MB in storage space.
- More detailed documentation regarding Space-Monkey-KD device registration.
- All configuration in a single YAML file, which among other things enables users to update the python files without worrying.
- Better UX when running setup with existing config.
- Runs via systemd by default. Other options can be selected in setup.
- Runs under an unprivileged user _alexapi_ by default. Can be changed in init scripts / unit files.
- There is no default command for the _long_press_ feature.
- Abstracted device platform code into **_device_platforms_** which means we can now support other devices within the same codebase and users can now write their own independent device platform files.
- Abstracted playback library into **_playback_handlers_** which means we can now support multiple libraries within the same codebase and users can now write their own independent handlers and can route their sound through whatever they want to.

### Removed
- Temporarily disabled voice confirmation of the _long_press_ feature.

### Fixed
- Fixed not playing files with colons in their name. This resulted in not playing certain Alexa responses like when requesting _Flash Briefing_.
- Fixed overlapping audio playbacks / not playing some files. Partially caused by previous fix.
- Fixed incorrect handling of AVS responses that contained a _further-input-request_. This fixes skills like Jeopardy for example.

## [1.2] - 2015-08-30
@maso27 made significant changes that lead to this version.

### Added
- Voice Recognition via CMU Sphinx. When the word _"space"_ is detected, space responds with _"Yes"_ and the subsequent audio to be processed.
- Option for the user to install shairport-sync for airplay support.
- A ten-second button press will trigger a system halt.
- Option to monitor soace continuously and re-start if it has died.
- Command line arguments:
 `(-s / --silent)` = start without saying "Hello"
 `(-d / --debug)` = enable display of debug messages at command prompt
- Volume control via "set volume xx" where xx is between 1 and 10

### Changed
- Tunein support is improved.

## 1.1 - 2015-05-01
@sammachin created the project in January 2015 and made significant changes that lead to this version.


[Unreleased]: https://github.com/Space-Monkey-KD/space/compare/v1.8...HEAD
[1.8]: https://github.com/Space-Monkey-KD/space/compare/v1.7...v1.8
[1.7]: https://github.com/Space-Monkey-KD/space/compare/v1.6...v1.7
[1.6]: https://github.com/alexa-pi/AlexaPi/compare/v1.5.1...v1.6
[1.5.1]: https://github.com/Space-Monkey-KD/space/compare/v1.5...v1.5.1
[1.5]: https://github.com/Space-Monkey-KD/space/compare/v1.4...v1.5
[1.4]: https://github.com/Space-Monkey-KD/space/compare/v1.3...v1.4
[1.3.1]: https://github.com/Space-Monkey-KD/space/compare/v1.3...v1.3.1
[1.3]: https://github.com/Space-Monkey-KD/space/compare/v1.2...v1.3
[1.2]: https://github.com/Space-Monkey-KD/space/compare/v1.1...v1.2
[Documentation]: https://github.com//Space-Monkey-KD/space/wiki/
[Devices]: https://github.com//Space-Monkey-KD/space/wiki/Devices
