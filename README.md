<p align="center">
<a href="https://github.com/hemantapkh/torrenthunt/stargazers">
<img src="https://img.shields.io/github/stars/hemantapkh/torrenthunt" alt="Stars">
</a>
<a href="https://github.com/hemantapkh/torrenthunt/fork">
<img src="https://img.shields.io/github/forks/hemantapkh/torrenthunt.svg" alt="Forks"/>
</a>
<img src="https://visitor-badge.laobi.icu/badge?page_id=hemantapkh.torrenthunt" alt="visitors" />
<a href="https://github.com/hemantapkh/torrenthunt/graphs/contributors">
<img src="https://img.shields.io/github/contributors/hemantapkh/torrenthunt.svg" alt="Contributors" />
<a href="https://www.youtube.com/c/H9TechYouTube?sub_confirmation=1">
<img src="https://img.shields.io/badge/YouTube-H9-red" alt="Subscribe my channel H9"/>
</a>
</a>
</p>

<p align="center">
<img src="images/TorrentHunt.jpg" align="center" height=365 alt="Torrent Hunt Bot" />
</p>

<p align="center">
<a href="https://t.me/torrenthuntbot?start=githubReadme">
<img src='https://img.shields.io/endpoint?logo=telegram&style=for-the-badge&url=https%3A%2F%2Fhemantapokharel.com.np%2Fshields%2FTorrentHunt%2F'>
</a>
<a href="https://t.me/h9youtube">
<img src='https://img.shields.io/endpoint?logo=telegram&style=for-the-badge&url=https%3A%2F%2Fhemantapokharel.com.np%2Fshields%2Fh9youtube%2F'>
</a>
</P>
<h1 align='center'>🔍 Torrent Hunt Bot</h1>

<p align="center">
Torrent Hunt Bot is a telegram bot to search and explore torrents from different sources. It can show you the result of your query in a snap. Furthermore, you can explore top, trending, & popular torrents and browse torrents of a certain category. 
</P>

# 🌐 Supported Torrent Sources

- [1337x.to](https://1337x.to/)
- [The pirate bay](https://thehiddenbay.com/)
- [Torrent Galaxy](https://torrentgalaxy.to/)
- [RARBG](https://rargb.to/)
- [Nyaa](https://nyaa.si/)
- [YTS](https://yts.mx/)
- [Ez Tv](https://eztv.re/)
- [Tor lock](https://www.torlock.com/)
- [ET Tv](https://www.ettvcentral.com/)


# ⛲ Features

- Superfast and good pagination
- Supports 18 different languages
- Custom query search
- Explore trending, popular, and top torrents
- Browse torrents of a certain category
- Get info, images, magnet link and  .Torrent file of the torrent
- Get the shortened URL of the magnet link
- Supports inline query with thumbnail
- Restriction mode to hide explicit content
- Directly add the torrent in your [seedr](https://seedr.cc) account
- Auto typo correction and suggestions

# 🗣️ Languages

Torrent Hunt Bot can talk in 19 different languages.

- Arabic (Added by [Omar Khalid](https://github.com/omvrkhvlid))
- Bengali (Checked and fixed by [sobuj53](https://github.com/sobuj53)) 
- Belarusian
- Catalan
- Dutch
- English (Original)
- French (Checked and fixed by [xav35000](https://github.com/xav35000))
- German
- Hindi
- Italian (Checked and fixed by [bacchilega](https://github.com/bacchilega)) 
- Korean
- Malay
- Nepali
- Polish (VChecked and fixed by [Oskar](https://discordapp.com/users/171642532818714624))
- Portuguese
- Russian
- Spanish
- Turkish (Checked and fixed by [Berce](https://github.com/must4f))
- Ukrainian

`Unverified languages are translated with Google Translator and may contain errors. Feel free to create a Pull Request with modifications to the language.json file.`

**While making a PR, make sure to add yourself and a verified tag on the language.**

---

## 🔑 License

**If you want to host this bot for public use, you shall not remove or replace our links.**

See [LICENSE](LICENSE) for more information.

---

## ⚒️ Deployment

* Clone the repository, create a virtual environment, and install the requirements

    ```bash
    git clone https://github.com/hemantapkh/torrenthunt && virtualenv env && source env/bin/activate && cd torrenthunt && pip install -r requirements.txt
    ```

* Host the [Torrents-API](https://github.com/Ryuk-me/Torrents-Api) on your own server for better performance or leave it default. This API will be used for inline query only.

* Edit the [src/sample-config.json](src/sample-config.json) file and rename it to `config.json`

    <details>
    <summary>⚙️ Click here to see a sample config file</summary>
    
    ```json
    {
    "botToken": "<BOT Token>",

    "connectionType": "polling",

    "webhookOptions":{
        "webhookHost": null,
        
        "webhookPort": null,
        
        "webhookListen": "0.0.0.0",
        
        "sslCertificate": null,
        
        "sslPrivateKey": null
    },
    
    "adminId" : "<Admin UserId>", 

    "database": "torrenthunt.sqlite",

    "magnetDatabase": "magnets.sqlite",

    "cache": "cache",

    "cacheTime": 86400,

    "language": "language.json",

    "apiLink": "https://torrents-api.ryukme.repl.co/api" 
    }
    ```
    </details>

* Run the [migration.py](migrations.py) file to open a database.

    ```python
    python migrations.py
    ```
* Now, start the bot polling

    ```python
    python torrenthunt.py
    ```

---

## 🚀 Webhook Deployment

While polling and webhooks both accomplish the same task, webhooks are far more efficient. Polling sends a request for new events (specifically, Create, Retrieve, and Delete events, which signal changes in data) at a predetermined frequency and waits for the endpoint to respond whereas, webhooks only transfer data when there is new data to send, making them 100% efficient. That means that polling creates, on average, 66x more server load than webhooks. ([r](https://blog.cloud-elements.com/webhooks-vs-polling-youre-better-than-this))

- Generate an SSL certificate

    ```bash
    >> openssl genrsa -out sslPrivateKey.pem 2048
    >> openssl req -new -x509 -days 3650 -key sslPrivateKey.pem -out sslCertificate.pem
    ```

    *"Common Name (e.g. server FQDN or YOUR name)" should be your Host IP.*

- Rename the [src/sample-config.json](src/sample-config.json) file  to `config.json` and set

    - **connectionType** = **webhook**
    - **webhookHost** = **IP/Host where the bot is running**
    - **webhookPort** = **PORT (Need to be opened)**
    - **webhookListen** = **0.0.0.0** or **IP address in some VPS**
    - **sslCertificate** = **Directory of SSL certificate**
    - **sslPrivateKey** = **Directory of SSL private key**

* And, start the aioHttp server.

    ```python
    python torrenthunt.py
    ```

---

## 🛺 Auto deployment on every push

You can set up GitHub actions to update the bot automatically on every push.

- Fork the repository on your GitHub account.

- Create a directory
    ```bash
    mkdir /opt/TorrentHunt && cd /opt/TorrentHunt
    ```

    *You should create a directory with the same name as above inside /opt, or edit the [deploy.yml](.github/workflows/deploy.yml) and [deployScript.sh](.github/workflows/deployScript.sh)*

- Create a virtual environment in the directory with name `env`

    ```bash
    virtualenv env
    ```

- Clone the repository and install the requirements in the virtual environment

    ```bash
    git clone https://github.com/hemantapkh/TorrentHunt && cd TorrentHunt && source /opt/TorrentHunt/env/bin/activate && pip install -r requirements.txt
    ```

- Create a database and move the database into `/opt/TorrentHunt`

    ```bash
    python migrations.py && mv database.sqlite /opt/TorrentHunt
    ```

- Generate SSH keys for your VPS and keep the private key in your GitHub secrets

    - Create the ssh key pair using the `ssh-keygen` command. You must leave the passphrase empty while generating the SSH key.
    - Copy and install the public ssh key on the server using `sh-copy-id -i your_public_key user@host` command or add the content of the public key in `~/.ssh/authorized_keys`.
    - Now, copy the content of the private key and paste it on your GitHub secrets with the name `SSHKEY`. *(Repository settings >> secrets >> New repository secret)*

- Create another GitHub secret with name `HOST` and save your Host IP.

- Rename the [src/sample-config.json](src/sample-config.json) file  to **config.json** and set

    - **database** = **/opt/TorrentHunt/database.sqlite**
    - If you are using webhooks, copy the SSL certificate and private key in `/opt/TorrentHunt` and set
        - **sslCertificate** = **/opt/TorrentHunt/sslCertificate.pem**
        - **sslPrivateKey** = **/opt/TorrentHunt/sslPrivateKey.pem**

- Copy the content of the edited config.json and save it on your repository secrets with name `CONFIG`. Don't forget to wrap the content of config file with single quotes like this `'Content of config.json'`.

- And, start the bot.

    ```bash
    source /opt/TorrentHunt/env/bin/activate && screen -dm python /opt/TorrentHunt/TorrentHunt/torrenthunt.py
    ```

Now, every time you push on the `main` branch, the bot automatically gets updated.

---

## 💚 Contributing

Any contributions you make are **greatly appreciated**.

For minor fix, you can directly create a pull request and for adding a new feature, let's first discuss it in our [telegram group](https://t.me/h9discussion) or in [GitHub Discussion](https://github.com/hemantapkh/torrenthunt/discussions).

**🙏 Special thanks to [Ryuk-me](https://github.com/Ryuk-me) for creating [Torrents-Api](https://github.com/Ryuk-me/Torrents-Api) which is used for inline query in Torrent Hunt.**

-----
❇️ Made using [1337x](https://github.com/hemantapkh/1337x) and [pyTelegramBotApi](https://github.com/eternnoir/pyTelegramBotAPI) in Python💙 by [Hemanta Pokharel](https://github.com/hemantapkh/) [[✉️](mailto:hemantapkh@yahoo.com) [💬](https://t.me/hemantapkh) [📺](https://youtube.com/h9youtube)]
