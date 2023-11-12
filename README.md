### Project description:
This is VPN Service for - Protect Your Online Privacy and Security. VPN Service - ultimate solution for safeguarding your online privacy and enhancing your digital security.In an age where  digital footprints are constantly expanding, it's more crucial than ever to keep your online activities safe from prying eyes and potential threats.
***

### For starting through Docker:

## 1. Clone project:

```bash
git clone https://github.com/stepanenko-ya/vpn.git
```

## 2. Build Docker images:

```bash
docker-compose build
```

## 3. Run containers:

```bash
docker-compose up
```
***


### For starting through environment:

## 1. Create Virtual Environment:

```bash
python3 -m pip install --user virtualenv
```

```bash
virtualenv -p python3 venv
or
python3 -m virtualenv venv
```

```bash
source venv/bin/activate
```

***


## 2. Clone project and install all libraries:

```bash
git clone https://github.com/stepanenko-ya/vpn.git
```

```bash
cd vpn/
```

```bash
pip3 install -r requirements.txt
```

***


## 3. Apply migrations and Run server:

<br>

```bash
python vpn/manage.py migrate
```

```bash
python vpn/manage.py runserver
```

***


### RUN TESTS:

```bash
python vpn/manage.py test
```

***
