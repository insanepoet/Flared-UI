<div id="top"></div>

# Flared-UI - Effortless Cloudflare Tunnel Management for Your Homelab

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![Build Status][build-shield]][build-url] <div align="center">(coming soon)</div>

<br />
<div align="center">
  <a href="https://github.com/insanepoet/Flared-UI">
    <img width="140" alt="Flared-UI Logo" src="https://github.com/insanepoet/Flared-UI/blob/dev/FlaredUI/Static/img/FlaredUI_Logo(WhiteCloud).png?raw=true">
  </a>

  <p align="center">
    **Empowering your homelab with secure and accessible services.**
    <br />
    <a href="https://github.com/insanepoet/Flared-UI/issues">Report Bugs | Request Features</a>
  </p>
</div>

## Table of Contents

- [About Flared-UI](#about-flared-ui)
  - [Key Features](#key-features)
  - [Service Discovery](#service-discovery)
- [Getting Started](#getting-started)
  - [Installation](#installation)
- [Usage](#usage)
- [Future Development](#future-development)
- [Contributing](#contributing)
- [Contact](#contact)
- [Acknowledgments](#acknowledgments)
- [Additional Resources](#additional-resources)

## About Flared-UI



Flared-UI simplifies the setup and management of Cloudflare Tunnels for your homelab. Born out of a desire to help friends easily secure and access their services, Flared-UI has evolved into a powerful yet intuitive tool.

### Key Features

- **Automated Tunnel Creation:**  Effortlessly create secure tunnels with minimal configuration.
- **Service Discovery:**  Automatically identify services running in your homelab.
- **Customizable YAML Configuration:**  Fine-tune settings for each exposed service.
- **Real-time Monitoring & Logs:**  Track tunnel status and troubleshoot issues with detailed logs.
- **User-friendly Interface:**  Intuitive web dashboard for managing your tunnels.

### Service Discovery

Flared-UI supports service discovery for a wide range of environments, including:

- **Bare-Metal Applications:** Web servers (Nginx, Apache), personal portals (OwnCloud), and more.
- **Containerized Applications:** Docker, Kubernetes, Podman, TrueNAS, Unraid.
- **Virtualized Applications:** ProxMox, ESXi, Nutanix, OpenStack, TrueNAS, Unraid, XCP, Xen.

## Getting Started

**Most users:**  Add a Flared-UI container image to your existing setup. (See detailed instructions in the Wiki).

**Manual Installation:** Follow the step-by-step guide in our [Wiki](link-to-your-wiki).

### Installation (Quick Start)

1. **Prerequisites:** Ensure you have `cloudflared` installed and configured.
2. **Clone Repository:** `git clone https://github.com/insanepoet/Flared-UI.git`
3. **Install Dependencies:** `pip install -r requirements.txt`
4. **Run:** `flask run`

## Usage

[Include screenshots or GIFs demonstrating common use cases]

*Describe how to interact with the Flared-UI dashboard, create tunnels, manage services, and view logs.*

## Future Development

Flared-UI is an evolving project, and I'm committed to adapting it to the latest changes in [Cloudflared](https://github.com/cloudflare/cloudflared) while actively considering user feedback and feature requests.



While the initial focus has been on creating a streamlined and intuitive user interface for managing Cloudflare Tunnels locally, several exciting enhancements are on the horizon. These include:



### Enhanced Service Discovery: 

_Expanding the range of supported services and network protocols, making it even easier for users to discover and expose applications running on their homelabs._

    

### Cloudflare API Integration: 

_Once the [stable release of Cloudflare's Python SDK 3.x](https://github.com/cloudflare/python-cloudflare/discussions/191) becomes available, the application will gain seamless integration with the Cloudflare API, allowing for direct management of DNS records, tunnel configuration, and other account-level settings._



### Extensibility through Plugins: 

_The introduction of a plugin system will enable developers to tailor Flared-UI to their unique requirements. This will open up opportunities for custom service discovery methods, specialized management features, and integrations with other tools and platforms._



### Community Collaboration: 

_Pull requests for new managers, discovery methods, and other enhancements are highly encouraged! Your contributions can help shape the future of Flared-UI and make it an even more valuable tool for the community._



### Additional Feature Requests: 

_I'm always open to hearing your ideas for new features or improvements. If you have a suggestion, please don't hesitate to reach out and share it!_



By fostering a collaborative environment and staying responsive to user needs, I aim to ensure that Flared-UI remains a simple solution for managing Cloudflare Tunnels in your homelab.

<p align="right">(<a href="#top">back to top</a>)</p>

## Contributing

Your contributions are welcome! Please see our [Contribution Guidelines](.github/CONTRIBUTING.md) for details.

## Contact

Rory Fincham (aka Insanepoet)

- LinkedIn: https://www.linkedin.com/in/rory-fincham/
- Discord: https://discord.gg/8F3fTJ9Qcc
- Email: me@rfincham.com

## Acknowledgments

* Cloudflare
* Choose an Open Source License
* Img Shields

## Additional Resources

- [Changelog](.github/CHANGELOG.md)
- [License](LICENSE)
- [Security Policy](.github/SECURITY.md)
- [Code of Conduct](.github/CODE_OF_CONDUCT.md)

[build-shield]: https://img.shields.io/badge/build-passing-brightgreen
[build-url]: #
[contributors-shield]: https://img.shields.io/github/contributors/insanepoet/Flared-UI?style=for-the-badge&color=%23f38020
[contributors-url]: https://github.com/insanepoet/Flared-UI/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/insanepoet/Flared-UI?style=for-the-badge&color=%23f38020
[forks-url]: https://github.com/insanepoet/Flared-UI/network/members
[stars-shield]: https://img.shields.io/github/stars/insanepoet/Flared-UI?style=for-the-badge&color=%23f38020
[stars-url]: https://github.com/insanepoet/Flared-UI/stargazers
[issues-shield]: https://img.shields.io/github/issues/insanepoet/Flared-UI?style=for-the-badge&color=%23f38020
[issues-url]: https://github.com/insanepoet/Flared-UI/issues
[license-shield]: https://img.shields.io/github/license/insanepoet/Flared-UI?style=for-the-badge&color=%23f38020
[license-url]: https://github.com/insanepoet/Flared-UI/blob/master/LICENSE
