# QandA-vietnam
Question and Answer - discuss for vietnamese people

## Technologies
- Backend: Python3 (v3.8), Django framework (version 3.1.3)

## Runs

### Server backend
**Clone repository**

        https://github.com/sLeeNguyen/QandA-vietnam.git
        cd QandA-vietnam
        
**Create virtualenv environment**

        python3 -m venv ./venv
        source venv/bin/activate
        
**Install libraries**

        pip install -r requirements.txt 

**Migrate database**

	python manage.py makemigrations
	python manage.py migrate

**And run server**

        python manage.py runserver
