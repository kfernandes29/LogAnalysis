# Log Analysis Project

## Project Description

This script will print out results from three queries against the database.

1. What are the most popular three articles of all time? Which articles have been accessed the most? Present this information as a sorted list with the most popular article at the top.

2. Who are the most popular article authors of all time? That is, when you sum up all of the articles each author has written, which authors get the most page views? Present this as a sorted list with the most popular author at the top.

3. On which days did more than 1% of requests lead to errors? The log table includes a column status that indicates the HTTP status code that the news site sent to the user's browser.

## Requirements

* [Python 3](http://www.python.org)
* [Vagrant](https://www.vagrantup.com/downloads.html)
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)
* [PostgreSQL](http://www.postgresql.org)

* [Vagrantfile](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f73b_vagrantfile/vagrantfile)
* [newsdata.zip](https://d17h27t6h515a5.cloudfront.net/topher/2016/August/57b5f748_newsdata/newsdata.zip)

## Setup

1. Install Vagrant and Virtual Box on your computer
2. Download the Vagrantfile and place it in a new directory
3. Open Terminal and change directory to the folder containing the Vagrant file ```cd <folder with Vagrantfile>```
4. Still in Terminal, type ```vagrant up``` and wait a couple of minutes as the virtual machine is downloaded and set up
5. Extract the contents of the newsdata.zip file to the ```/vagrant``` folder that has been created
6. Back in Terminal, type ```vagrant ssh``` to log in to your virtual machine
7. Type ```psql -d news -f newsdata.sql``` in the Terminal to set up the database

## Run

Open your Terminal and run the following commands from the directory containing the contents of this repo.

1. Boot up the VM (Virtual Machine)
```
vagrant up
```

2. Log in to the VM
```
vagrant ssh
```

3. Change directory
```
cd /vagrant
```

4. Run the log.py script
```
python3 log.py
```

## Expected Output

The following should be returned after a successful run of the script.

```
What are the three most popular articles of all time?


Article: Candidate is jerk, alleges rival | Views: 338647
Article: Bears love berries, alleges bear | Views: 253801
Article: Bad things gone, say good people | Views: 170098


Who are the most popular article authors of all time?


Author: Ursula La Multa | Views: 507594
Author: Rudolf von Treppenwitz | Views: 423457
Author: Anonymous Contributor | Views: 170098
Author: Markoff Chaney | Views: 84557


On which days did more than 1% of requests lead to errors?


Date: Jul 17, 2016 | Errors Percentage: 2.28%

```

## Views

The following views will be created automatically upon running the log.py script.

* ```article_views``` is used to return the number of log results for each article.

```sql
CREATE OR REPLACE VIEW article_views AS
    SELECT title, author, COUNT(title) as views
    FROM articles, log
    WHERE log.path LIKE CONCAT('%', articles.slug)
    GROUP BY title, author
    ORDER BY views DESC;
```

* ```author_views``` is used to return the total article views by an author.

```sql
CREATE OR REPLACE VIEW author_views AS
    SELECT name, SUM(article_views.views) AS total
    FROM article_views, authors
    WHERE authors.id = article_views.author
    GROUP BY authors.name
    ORDER BY total DESC;
```

* ```requests_total``` is used to return the total number of requests for each day.

```sql
CREATE OR REPLACE VIEW requests_total AS
    SELECT COUNT(*) as total, DATE(time) AS day
    FROM log
    GROUP BY day
    ORDER BY day DESC;
```

* ```requests_errors``` is used to return the number of requests that led to errors for each day.

```sql
CREATE OR REPLACE VIEW requests_errors AS
    SELECT COUNT(*) as total, DATE(time) AS day
    FROM log
    WHERE status != '200 OK'
    GROUP BY day
    ORDER BY total DESC;
```

* ```requests_errors_percent``` is used to return the percentage of requests that led to an error in a day.

```sql
CREATE OR REPLACE VIEW requests_errors_percent AS
    SELECT requests_total.day,
        round((100.0*requests_errors.total)/requests_total.total,2)
        AS percentage
    FROM requests_errors, requests_total
    WHERE requests_errors.day=requests_total.day;
```

## Credits

* [Udacity Fullstack Nanodegree](https://classroom.udacity.com/nanodegrees/nd004)
