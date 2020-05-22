<!-- PROJECT -->
<br />

  <h3 align="center">PevFTPClient</h3>

  <p align="center">
   a self made FTP client built on python
    <br />
    <a href="https://github.com/Peviroy/PevFTPClient"><strong>Explore the docs »</strong></a>
    <br />

</p>

## About The Project

This project develops ftp client applications based on socket streaming characters, basically implements the six major functions of **CWD, LIST, GET, DELETE, and UPLOAD**; and develops the web terminal based on **Flask**.



### Tested on

* Ubuntu Linux 
* Manjaro Linux 18.04

Since we simply only implemented the client end, we adopted an open source [ftp server](https://github.com/jacklam718/ftp/), which is **based on Linux file system**. Therefore we only test this project on Linux.



### Directory tree

```bash
.
├── commandlineEdition
│   └── server-opensource
└── webEdition
    ├── FTPClient
    │   └── __pycache__
    ├── server-opensource
    ├── static			 		-[FLASK] static files
    └── templates				-[FLASK] html templates
```


### Built With

* [Pytorch](https://github.com/pytorch/pytorch)
* [Flask]()

### Requirement 

* Flask

#### versions  used

​	There is no feature code in this project, so any release version is ok. Here is my version below:

```
Flask==1.1.2
```

### Some Result

#### commandline mode

<img src="https://i.loli.net/2020/05/22/2tjuCqSIroi3y6L.png" alt="image-20200522131725516" style="zoom: 67%;" />

#### web mode

<img src="https://i.loli.net/2020/05/22/kwjgXSM91eNyBFZ.png" alt="image-20200522131815725" style="zoom:67%;" />

## Getting Started

### Installation

1. Clone the repo

```sh
git https://github.com/Peviroy/PevFTPClient.git
```

2. Install requirements

```sh
cd PevFTPClient
pip install -r requirements 
```

### Run

#### `commandline mode`

1. Start server firstp

   ```bash
   cd commandlineEdition/server-opensource # in project root
   python ftp_server.py
   ```

2. Start client latter

   ```bash
   #According to the output of server, determining the host address and port
   cd ..
   python ftp_clientx.py -s 127.0.1.1 -P 8899
   ```

3. Input username and password:
   <img src="https://i.loli.net/2020/05/22/2tjuCqSIroi3y6L.png" alt="image-20200522131725516" style="zoom: 50%;" />

   Since ftp_server doesn't specify users; so it's free to type you information;

#### `web mode`

1. Start server first

   ```bash
   cd webEdition/server-opensource # in project root
   python ftp_server.py
   ```

2. Start the client latter

   ```bash
   cd ..
   python app.py -s 127.0.1.1 -P 8899 -u Pevrioy -p 123
   ```

   Because the web side is still in the prototype, **no login page is set**, so you need to specify the username and password first;

3. Visit the website
   ![image-20200522133530774](https://i.loli.net/2020/05/22/IpyqfNieDXWH6G9.png)

4. The operation mode is the same as the command line mode, enter the instruction in the input box, press Enter or press the button to execute:
   <img src="https://i.loli.net/2020/05/22/kwjgXSM91eNyBFZ.png" alt="image-20200522131815725" style="zoom: 50%;" />

   

## Contact

- [email](https://twitter.com/twitter_handle) - peviroy@outlook.com

Project Link: [https://github.com/Peviroy/PevFTPClient](https://github.com/Peviroy/PevFTPClient)

