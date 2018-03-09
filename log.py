#! /usr/bin/env python3

import psycopg2
import psycopg2.extras

# Create variable for database name
db_name = 'news'


def main():
    # Create views
    create_views()
    # Query 1
    print("\n\nWhat are the three most popular articles of all time?\n\n")
    get_popular_articles()
    # Query 2
    print("\n\nWho are the most popular article authors of all time?\n\n")
    get_popular_authors()
    # Query 3
    print("\n\nOn which days did more than 1% of requests lead to errors?\n\n")
    get_most_errors_percent()

# Create views that will be used in our queries


def create_views():
    # Connect to database
    db = psycopg2.connect(database=db_name)
    # Cursor for database queries
    c = db.cursor()
    # Create view to return article views
    c.execute('''
        CREATE OR REPLACE VIEW article_views AS
            SELECT title, author, COUNT(title) as views
            FROM articles, log
            WHERE log.path LIKE CONCAT('%', articles.slug)
            GROUP BY title, author
            ORDER BY views DESC;
    ''')
    # Create view to return all article views by an author
    c.execute('''
        CREATE OR REPLACE VIEW author_views AS
            SELECT name, SUM(article_views.views) AS total
            FROM article_views, authors
            WHERE authors.id = article_views.author
            GROUP BY authors.name
            ORDER BY total DESC;
    ''')
    # Create view to retrieve total requests for a day
    c.execute('''
        CREATE OR REPLACE VIEW requests_total AS
            SELECT COUNT(*) as total, DATE(time) AS day
            FROM log
            GROUP BY day
            ORDER BY day DESC;
    ''')
    # Create view to retrieve requests that lead to errors for each day
    c.execute('''
        CREATE OR REPLACE VIEW requests_errors AS
            SELECT COUNT(*) as total, DATE(time) AS day
            FROM log
            WHERE status != '200 OK'
            GROUP BY day
            ORDER BY total DESC;
    ''')
    # Create view to retrieve days with percentage of
    # requests that led to errors
    c.execute('''
        CREATE OR REPLACE VIEW requests_errors_percent AS
            SELECT requests_total.day,
                round((100.0*requests_errors.total)/requests_total.total,2)
                AS percentage
            FROM requests_errors, requests_total
            WHERE requests_errors.day=requests_total.day;
    ''')
    # Commit changes
    db.commit()
    # Close database connection
    db.close()

# Execute query passed into function and return results


def execute_query(query):
    # Connect to database
    db = psycopg2.connect(database=db_name)
    # Cursor for database queries
    c = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Query most popular article authors of all time
    try:
        c.execute(query)
    except Exception as e:
        print(e)
        raise
    # Store results in a variable to be returned
    results = c.fetchall()
    # Close database connection
    db.close()
    # Return results
    return results

# Get the three most popular articles


def get_popular_articles():
    # SQL query string
    query = '''
        SELECT title, views
        FROM article_views
        LIMIT 3;
    '''
    # Results from SQL query
    results = execute_query(query)
    # Print results to terminal
    for row in results:
        print("Article: {} | Views: {}".format(
            row['title'], row['views']))

# Get the most popular authors based on article views


def get_popular_authors():
    # SQL query
    query = '''
        SELECT *
        FROM author_views;
    '''
    # Results from SQL query
    results = execute_query(query)
    # Print results to terminal
    for row in results:
        print("Author: {} | Views: {}".format(
            row['name'], row['total']))

# Get the days where more than 1% of requests resulted in errors


def get_most_errors_percent():
    # SQL query
    query = '''
        SELECT to_char(day, 'Mon DD, YYYY') AS day, percentage
        FROM requests_errors_percent
        WHERE percentage > 1.0
        GROUP BY day, percentage
        ORDER BY percentage DESC;
    '''
    # Results from SQL query
    results = execute_query(query)
    # Print results to terminal
    for row in results:
        print("Date: {} | Errors Percentage: {}%\n\n".format(
            row['day'], row['percentage']))


# Start script
if __name__ == '__main__':
    main()
