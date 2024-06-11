<div id="top"></div>

# Flared-UI: Simplify Your Cloudflare Tunnel Management

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![Apache2 License][license-shield]][license-url]

<div align="center">
  <a href="https://github.com/insanepoet/Flared-UI">
    <img width="140" alt="Flared-UI Logo" src="https://github.com/insanepoet/Flared-UI/blob/dev/FlaredUI/Static/img/FlaredUI_Logo(WhiteCloud).png?raw=true">
  </a>

  <p align="center">
    Your Homelab, Tunneled by [Cloudflare](https://cloudflare.com) with Ease
    <br />
    <a href="https://github.com/insanepoet/Flared-UI/issues">Report Bugs & Suggest Features</a>
    <br />
    <a href="#getting-started">Quick Start Guide</a> | 
    <a href="https://github.com/insanepoet/Flared-UI/wiki">Complete Documentation</a> 
  </p>
</div>

## About Flared-UI
Frustrated with tabbing back and forth or manually configuring Cloudflare Tunnels for your homelab services? Flared-UI is your solution. Born from real-world needs, Flared-UI makes it a breeze to discover, configure, and manage your Cloudflare Tunnels.
<!-- UPDATE -->
<div align="center">
  <a href="https://github.com/proffapt/PROJECT_NAME">
    <img width="80%" alt="image" src="https://user-images.githubusercontent.com/86282911/206632547-a3b34b47-e7ae-4186-a1e6-ecda7ddb38e6.png">
  </a>
</div>

_After helping several friends set up Cloudflare Tunnels for their homelabs, I realized that while the process isn't overly complex, a tool to simplify the configuration and generate the correct YAML files would make it much easier for them to manage their tunnels locally and secure their services._

_What began as a simple form to input services quickly evolved into a comprehensive tool that not only streamlines the initial setup but empowers users with ongoing control over their tunnels. The application includes a built-in service discovery mechanism, allowing users to easily identify and select the services running on their network that they wish to expose through Cloudflare. It generates an accurate YAML configuration file tailored to properly expose each service, eliminating the need for manual configuration and reducing the risk of errors. Additionally, the tool offers a user-friendly interface for starting, stopping, and monitoring tunnels, along with real-time log viewing for troubleshooting. By abstracting the complexities of cloudflared CLI commands, Flared-UI makes it accessible to users of all technical levels, enabling them to harness the power of Cloudflare Tunnels effortlessly._

**Key Features:**

* **Effortless Service Discovery:** Automatically identify web servers, personal portals, containerized apps (Docker, Kubernetes, etc.), and virtualized services on your network.
* **Zero-Config YAML Generation:**  Instantly create accurate YAML configuration files for each service, eliminating manual errors.
* **Intuitive Tunnel Management:** Start, stop, and monitor your tunnels through a user-friendly interface.
* **Real-Time Logs:** Troubleshoot issues with live log viewing.

<p align="right">(<a href="#top">back to top</a>)</p>

<div id="service-discovery"></div>

### Service Discovery Supports:
1. Bare-Metal Applications
    * `Webservers such as nginx/apache`
    * `Personal portals such as owncloud`
    * `Any Bare-Metal application with exposed ports (compliant with Cloudflare's Terms)`
2. Containerized Applications through the following managers
    * `Docker`
    * `Kubernetes`
    * `Podman`
    * `TrueNas`
    * `UnRaid`
3. Virtualized Applications through the following managers
    * `ProxMox`
    * `ESXi`
    * `Nutanix`
    * `OpenStack`
    * `TrueNas`
    * `UnRaid`
    * `XCP` and `Xen`


<p align="right">(<a href="#top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

Most Users will simply need to add one of the containerized images to their existing container solution.

<< Insert Instruction table here for basic instructions with link to wiki for detailed >> 

If you wish however to install the application manually please visit the wiki page here.


### Installation

<< Insert step by step walkthrough of installation >>

<p align="right">(<a href="#top">back to top</a>)</p>

### First - Run
On first load of the application you will be presented with an installation wizard (He has a staff and everything).

<!-- USAGE EXAMPLES -->
## Usage
<!-- UPDATE -->
<< Show useful examples of how the project can be used. >>
<p align="right">(<a href="#top">back to top</a>)</p>

<!-- Future -->
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
<!-- CONTACT -->

## Contact
<p>
Rory Fincham ( aka Insanepoet ) -
<a href="https://www.linkedin.com/in/rory-fincham/">
  <img align="center" alt="insanepoet's LinkedIn" width="22px" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/linkedin.svg" />
</a>
&nbsp;
<a href="https://discord.gg/8F3fTJ9Qcc">
  <img align="center" alt="Insanepoet Development Discord" width="22px" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/discord.svg" />
</a>
&nbsp;
<a href="mailto:me@rfincham.com">
  <img align="center" alt="insanepoet's mail" width="22px" src="https://raw.githubusercontent.com/edent/SuperTinyIcons/master/images/svg/email.svg" />
</a>
</p>

<p align="right">(<a href="#top">back to top</a>)</p>


<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

* [Cloudflare](https://Cloudflare.com)
* [Choose an Open Source License](https://choosealicense.com)
* [Img Shields](https://shields.io)
* [proffapt myReadme Template](https://github.com/proffapt/myREADME)
<!-- UPDATE -->

<p align="right">(<a href="#top">back to top</a>)</p>

## Additional documentation

  - [Changelogs](/.github/CHANGELOG.md)
  - [License](/LICENSE)
  - [Security Policy](/.github/SECURITY.md)
  - [Code of Conduct](/.github/CODE_OF_CONDUCT.md)
  - [Contribution Guidelines](/.github/CONTRIBUTING.md)

<p align="right">(<a href="#top">back to top</a>)</p>

<div id="getting-started"></div>

## Getting Started

### Quick Start (Containers):

[Instruction table for basic container setup]

**Need more details?** Visit our [Wiki]([https://github.com/insanepoet/Flared-UI/wiki](https://github.com/insanepoet/Flared-UI/wiki)) for comprehensive installation guides.


### Manual Installation (Advanced):

[Step-by-step installation instructions]


## Usage

[Code examples demonstrating typical usage scenarios]

**For a complete user guide, refer to the [Wiki]([https://github.com/insanepoet/Flared-UI/wiki](https://github.com/insanepoet/Flared-UI/wiki)).**

## Roadmap

Flared-UI is actively evolving. Here's what's on the horizon:

- **Enhanced service discovery** for a wider range of applications and protocols.
- **Cloudflare API integration** for seamless DNS management and more.
- **Extensible plugin system** for custom functionality. 
- **Your feedback is welcome!** Help us prioritize features through [issues and discussions](https://github.com/insanepoet/Flared-UI/issues).

## Contributing

We welcome contributions! See our [Contributing Guidelines]([https://github.com/insanepoet/Flared-UI/.github/CONTRIBUTING.md](https://github.com/insanepoet/Flared-UI/.github/CONTRIBUTING.md)) for details.



<!-- MARKDOWN LINKS & IMAGES -->

[contributors-shield]: https://img.shields.io/github/contributors/insanepoet/Flared-UI?style=flat&color=%23f38020
[contributors-url]: https://github.com/insanepoet/Flared-UI/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/insanepoet/Flared-UI?style=flat&color=%23f38020
[forks-url]: https://github.com/insanepoet/Flared-UI/network/members
[stars-shield]: https://img.shields.io/github/stars/insanepoet/Flared-UI?style=flat&color=%23f38020
[stars-url]: https://github.com/insanepoet/Flared-UI/stargazers
[issues-shield]: https://img.shields.io/github/issues/insanepoet/Flared-UI?style=flat&color=%23f38020
[issues-url]: https://github.com/insanepoet/Flared-UI/issues
[license-shield]: https://img.shields.io/github/license/insanepoet/Flared-UI?style=flat&color=%23f38020
[license-url]: https://github.com/insanepoet/Flared-UI/blob/master/LICENSE