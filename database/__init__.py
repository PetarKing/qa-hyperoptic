
"""
Database interactions
"""

from datetime import date
import psycopg2
import pandas as pd

pd.set_option('display.expand_frame_repr', False)
pd.set_option('display.max_rows', None)

# from config import config
 
def connect_to_jira():
    """ Connect to the Jira's PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        # params = config()
 
        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        # conn = psycopg2.connect(**params)
        conn = psycopg2.connect("host=jiradb.cfjieo6npcxv.eu-west-1.rds.amazonaws.com dbname=jira1 user=petar.nedeljkovic password=Viesh3o9haegheecae")
        # conn.set_client_encoding('UTF-16')

        # create a cursor
        cur = conn.cursor()
        return conn, cur
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def get_q_test_coverage_per_member(sprints, fit_app=False):
    conn, cur = connect_to_jira()
    results = 'ERROR'
    if (not conn):
        print('Failed to connect to the Jira DB')
    else:
        try:
            print('Getting QTest coverage stats')
            # By Sprints & Team-member
            query = '''
            SELECT A.assignee, A.count as Coverage, B.count as Load, round((cast(A.count as decimal)/cast(B.count as decimal))*100, 2) as Percentage, A.Sprint
            FROM
            (SELECT ji.assignee, COUNT(*), cf.STRINGVALUE as Sprint
            FROM remotelink rl
            LEFT JOIN jiraissue ji ON rl.issueid = ji.ID
            AND applicationname = 'qTest'
            AND ji.issuetype = '10002'
            INNER JOIN issuelink il
            ON il.destination = ji.id
            and il.source {1}
            INNER JOIN customfieldvalue cf ON (ji.ID=cf.ISSUE) 
            AND CUSTOMFIELD = 10104 AND cf.STRINGVALUE {0}
            GROUP BY Sprint, ji.assignee) A
            INNER JOIN (SELECT ji.assignee, COUNT(*), cf.STRINGVALUE as Sprint
            FROM jiraissue ji
            INNER JOIN customfieldvalue cf ON (ji.ID=cf.ISSUE) 
            AND ji.issuetype = '10002'
            AND CUSTOMFIELD = 10104 AND cf.STRINGVALUE {0}
            INNER JOIN issuelink il
            ON il.destination = ji.id
            and il.source {1}
            GROUP BY Sprint, ji.assignee) B
            ON A.Sprint = B.Sprint
            AND A.assignee = B.assignee
            '''.format('IN '+ str(tuple(sprints)) if len(sprints) > 1 else "= '" + sprints[0] + "'", "= 238952" if fit_app else "!= 238952")
            # print(query)
            df = pd.read_sql_query(query ,con=conn, index_col=None)
            print(df.head(100))
            results = df.to_html().replace('border="1" class="dataframe"', 'class="table"').replace(' style="text-align: right;"', '')
        except Exception as err:
            print('Query err', err)
    # close conn and cur
    cur.close()
    conn.close()
    return results
