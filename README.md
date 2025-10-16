# AutoCon 4 | WS:B2
### Design-Driven (Container)Labs and Change Validation

[Lab Guide](./docs/index.md) #TODO: Add GitHub Pages Link

## About the workshop
As part of the AutoCon 4 event, in this workshop we will attempt to dip our toes into the world of design-driven automation and test-driven change validation. If this sounds like a buzzword bingo, well, you are not wrong. The initial idea for this workshop was to create a lab that would focus on the four most used words in a previous AutoCon event: automation, design, containerlab, and testing (or at least this is how I remembered them as I couldn't find the original word cloud that inspired the idea).

Jokes aside, in this workshop we will be touching on the following components/tools:
- **Source of Truth (SoT)**: Nautobot
- **Design-Driven Automation**: Design Builder (a Nautobot App)
- **Digital Twin**: Containerlab
- **Network Testing**: NUTS
- **Change Validation**: Golden Config (another Nautobot App)

The goal is to create a pipeline of sorts that will allow us to try out changes, designs, and ideas in a safe environment, before we push them to production.


## Prerequisites
All workshop materials are available on Github: https://github.com/networktocode/autocon4-design-workshop (still working on a few minor things, but the main content is there).

In order to make things smoother (and avoid surprises like running out of Codespaces credits), Network to Code will provide a preconfigured cloud development environment (also available via browser). This includes all major dependencies, such as the software stack previously described, the Arista EOS Docker image that we'll be using for containerlab, etc. You’ll receive login instructions a few hours before the session.

What can you do ahead of time?
- **Create a Github account**: If you don't have one already, please create a Github account. You will need it to fork the original repository and work independently on your own copy of the lab. It won't hurt if you also create a Personal Access Token (PAT) as described in the respective section of the lab guide.

The following diagram shows the architecture of the lab environment.

![Lab Architecture](./lab_guide/images/lab_architecture.png)


## Authors
- Nikos Kallergis (@nkallergis)
- Allen Hogan (@alhogan)
- Israel Pineda (@igpaec)
- Jeff Kala (@jeffkala)