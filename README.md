# DBMS Project Team 2

## Phase - 1
- Login System 

## Creating virtual environment 

```sh
python3 -m venv env 
source env/bin/activate  
./env/Scipts/activate
```

## Installation 

### 1. Install `pkg-config` and MySQL development headers

If you're on a Debian-based system like Ubuntu, you can use `apt`:

```bash
sudo apt-get install pkg-config libmysqlclient-dev
```

For Red Hat-based systems like CentOS, use `yum`:

```bash
sudo yum install pkgconfig mysql-devel
```

For macOS, you can use Homebrew:

```bash
brew install pkg-config mysql-client
```

### 2. specify the `MYSQLCLIENT_CFLAGS` and `MYSQLCLIENT_LDFLAGS` environment variables as suggested in the error message. 

```bash
export MYSQLCLIENT_CFLAGS=`pkg-config --cflags mysqlclient`
export MYSQLCLIENT_LDFLAGS=`pkg-config --libs mysqlclient`
```

### 3. Retry the installation of `mysqlclient`

```bash
pip install mysqlclient
```

### 4. If the issue persists, consider using a different MySQL client for Python, such as `PyMySQL`, which is a pure Python MySQL client and doesn't require compiling native code:

```bash
pip install pymysql
```

```sh 
pip install -r requirements.txt

```

## Execution 

```sh 
python3 app.py 
```

or (if flask app vairable is already added to env):
```sh
flask run
```

or just . Debug mode: 
```sh
flask --app app --debug run
```



