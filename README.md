# Git-Mastery CLI App

Git-Mastery CLI to centralize and perform key operations of adapters.

## OS support

We currently support:

1. Windows `.exe` (amd64)
2. MacOS Homebrew (arm64)
3. Debian `.deb` and APT (amd64 and arm64)
4. Arch AUR (amd64)
5. Windows winget (amd64 and arm64)

If you wish to contribute to the packaging support, please reach out to the maintainers.

## Installation

Refer to the [installation guide](https://git-mastery.org/companion-app/index.html#installation-and-setup) for detailed instructions on how to install the Git-Mastery CLI app on your system.

## Local development

To develop the app locally, refer to the [development setup guide](https://git-mastery.org/developers/docs/getting-started/setup/) for detailed instructions on how to set up your development environment and contribute to the project.

## JSON verification output

Run `gitmastery verify --json` inside an exercise to get its grading result on
stdout:

```json
{"exercise_name": "under-control", "status": "Completed", "comments": []}
```

`status` is `Completed`, `Incomplete`, or `Error`. `comments` contains all grader
feedback in order, or an empty array when there is none. Diagnostic messages go
to stderr, so clients can parse the complete stdout as JSON.

Verification still saves progress and performs any configured remote submission.
Exit `0` means the command finished normally; read `status` to determine whether
the answer is correct. A failure before grading leaves stdout empty and exits
nonzero. A submission failure after grading retains the JSON result and exits
nonzero. Ordinary `gitmastery verify` keeps its existing text output.

See the [technical design](docs/verify-json-design.md) for the contract and desktop
integration plan.

## Publishing

Tag the PR with the `bump:{major | minor | patch}` label and the CI will automatically perform the publish.

A Github Actions workflow exists to automatically publish the changes to Homebrew.

Linux packaging is performed to Debian and Arch based distros. Notes can be
[found here.](https://woojiahao.notion.site/linux-packaging-226f881eda0580d68bc8dc6f8e1d5d0d?source=copy_link)

## Contributors

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://www.comp.nus.edu.sg/~damithch"><img src="https://avatars.githubusercontent.com/u/1673303?v=4?s=100" width="100px;" alt="Damith C. Rajapakse"/><br /><sub><b>Damith C. Rajapakse</b></sub></a><br /><a href="#mentoring-damithc" title="Mentoring">🧑‍🏫</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://blog.woojiahao.com/"><img src="https://avatars.githubusercontent.com/u/29497029?v=4?s=100" width="100px;" alt="Jiahao"/><br /><sub><b>Jiahao</b></sub></a><br /><a href="https://github.com/Git-Mastery/App/commits?author=woojiahao" title="Code">💻</a> <a href="https://github.com/Git-Mastery/App/commits?author=woojiahao" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/jovnc"><img src="https://avatars.githubusercontent.com/u/95868357?v=4?s=100" width="100px;" alt="jovnc"/><br /><sub><b>jovnc</b></sub></a><br /><a href="https://github.com/Git-Mastery/App/commits?author=jovnc" title="Code">💻</a> <a href="https://github.com/Git-Mastery/App/commits?author=jovnc" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://loh-jia-xin.vercel.app/"><img src="https://avatars.githubusercontent.com/u/122351681?v=4?s=100" width="100px;" alt="jia xin"/><br /><sub><b>jia xin</b></sub></a><br /><a href="https://github.com/Git-Mastery/App/commits?author=jiaxinnns" title="Code">💻</a> <a href="https://github.com/Git-Mastery/App/commits?author=jiaxinnns" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/VikramGoyal23"><img src="https://avatars.githubusercontent.com/u/105161079?v=4?s=100" width="100px;" alt="Vikram Goyal"/><br /><sub><b>Vikram Goyal</b></sub></a><br /><a href="https://github.com/Git-Mastery/App/commits?author=VikramGoyal23" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/desmondwong1215"><img src="https://avatars.githubusercontent.com/u/134215008?v=4?s=100" width="100px;" alt="Desmond Wong"/><br /><sub><b>Desmond Wong</b></sub></a><br /><a href="https://github.com/Git-Mastery/App/commits?author=desmondwong1215" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/SAN-MUYUN"><img src="https://avatars.githubusercontent.com/u/156393005?v=4?s=100" width="100px;" alt="SAN MUYUN"/><br /><sub><b>SAN MUYUN</b></sub></a><br /><a href="https://github.com/Git-Mastery/App/commits?author=SAN-MUYUN" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/TheMythologist"><img src="https://avatars.githubusercontent.com/u/29896527?v=4?s=100" width="100px;" alt="TheMythologist"/><br /><sub><b>TheMythologist</b></sub></a><br /><a href="https://github.com/Git-Mastery/App/commits?author=TheMythologist" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/seah-minlong"><img src="https://avatars.githubusercontent.com/u/86313670?v=4?s=100" width="100px;" alt="Minlong"/><br /><sub><b>Minlong</b></sub></a><br /><a href="https://github.com/Git-Mastery/App/commits?author=seah-minlong" title="Code">💻</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->
<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->
