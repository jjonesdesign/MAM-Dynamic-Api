# MAM Dynamic API  

## Overview  
**MAM Dynamic API** is a Python-based Docker container designed to automate the updating and maintenance of MyAnonamouse.net Dynamic IP changes. This ensures that VPN clients maintain an updated authentication cookie, allowing seamless authorization for torrent downloaders without manual intervention.  

## Features  
- Automatically updates MyAnonamouse.net Dynamic IP changes  
- Ensures VPN clients maintain an active authentication cookie  
- Seamless integration with torrent downloaders  
- Dockerized for easy deployment  

## Installation  

### Prerequisites  
- Docker installed on your system  
- A configured Gluetun container for VPN connectivity  

### Docker Compose Example (Gluetun)
To deploy **MAM Dynamic API**, use the following `docker-compose.yml` example:  

```yaml
services:
  gluetun:
    container_name: gluetun
    {Your Gluetun Config}

  mamdynamicapi:
    image: jjonesdesign/mam-dynamic-api:latest
    container_name: mam-dynamic-api
    network_mode: "service:gluetun"
    volumes:
      - /your/config/directory/mamdynamicapi:/config
    environment:
      - MAM_ID="{Your MAM ID}"
```

## Configuration  

### Environment Variables  
| Variable | Description |
|----------|------------|
| `MAM_ID` | Your MyAnonamouse.net user ID. Required for authentication and IP updates. (Can be removed after initial setup) |

### Volume Mapping  
| Host Path | Container Path | Description |
|-----------|---------------|-------------|
| `/your/config/directory/mamdynamicapi` | `/config` | Directory for storing configuration files. |
**Note:** Some may use the default `./config:/config` for the volume mapping.

## Usage  
Once deployed, the container will automatically update your MyAnonamouse.net authentication cookie whenever your dynamic IP changes, ensuring uninterrupted access for your torrent downloader.  

## Support & Contributions  
If you encounter any issues or have suggestions, feel free to submit an issue or contribute via pull requests.  

[![Buy Me a Coffee](https://img.buymeacoffee.com/button-api/?text=Buy%20Me%20a%20Coffee&emoji=☕&slug=jjonesdesign&button_colour=FFDD00&font_colour=000000&font_family=Arial&outline_colour=000000&coffee_colour=ffffff)](https://buymeacoffee.com/jjonesdesign)

## License  
This project is licensed as described in the LICENSE file.  