#!/usr/bin/env python
# coding: utf-8
# Importing libraries
# In[2]:


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
import missingno as msno
from textwrap import wrap

# loading and cleaning the data
# In[3]:


transaction_df = pd.read_excel('Transactions.xlsx')
transaction_df.head()

# Inspecting and Imputing missing values
# In[4]:


print(transaction_df.isnull().values.sum())
transaction_df=transaction_df.replace("",np.NaN)
transaction_df=transaction_df.fillna(transaction_df.mean())
print(transaction_df.isnull().values.sum())


# In[5]:


print(transaction_df.info())
for col in transaction_df.columns:
    if transaction_df[col].dtypes=='object':
        transaction_df[col]=transaction_df[col].fillna(transaction_df[col].value_counts().index[0])
        
print(transaction_df.isnull().values.sum())

# Assigning cohorts
# In[6]:


#date time based cohort: 1 day of month
def get_month(x):
    return dt.datetime(x.year,x.month,1)
#creating transaction_date column based on month and storing in TransactionMonth
transaction_df['TransactionMonth']=transaction_df['transaction_date'].apply(get_month)
#group by customerid and select invoice month value
grouping=transaction_df.groupby('customer_id')['TransactionMonth']
#Assigning cohort
transaction_df['CohortMonth']=grouping.transform('min')
#Printing
print(transaction_df.head())


# In[8]:


#getting the integer values of years, months and date for transaction and cohort dates
def get_date_int(df, column):
    year=df[column].dt.year
    month=df[column].dt.month
    day=df[column].dt.day
    return year,month,day
#getting date from 'InvoiceDay' column
transaction_year, transaction_month, _=get_date_int(transaction_df,'TransactionMonth')
#getting date from 'CohortDay' column
cohort_year, cohort_month, _=get_date_int(transaction_df,'CohortMonth')


# In[9]:


#difference between transaction and cohort year
years_diff=transaction_year-cohort_year
#difference between transaction and cohort month
months_diff=transaction_month-cohort_month
#extracting the difference and adding "+1" so that first month is marked as 1 instead of 0
transaction_df['CohortIndex']=years_diff*12+months_diff+1
print(transaction_df.head(5))

# creating pivot by adding cohort month to index, cohort index to columns and customer id to values 
# In[12]:


#counting active users from cohort
grouping=transaction_df.groupby(['CohortMonth','CohortIndex'])
#counting no. of unique customer id's in each cohort
cohort_data=grouping['customer_id'].apply(pd.Series.nunique)
cohort_data=cohort_data.reset_index()
#Assigning column names
cohort_counts=cohort_data.pivot(index='CohortMonth',columns='CohortIndex',values='customer_id')
#printing
cohort_data.head()

# calculating retention rate
# In[23]:


cohort_sizes=cohort_counts.iloc[:,0]
retention=cohort_counts.divide(cohort_sizes,axis=0)
#convrting retention rate into percentage and rounding off
retention.round(3)*100

# Visualisation
# In[30]:


plt.figure(figsize=(16, 10))
plt.title('retention rate in percentage: Monthly Cohorts', fontsize = 14)
sns.heatmap(retention.round(3)*100, annot = True,vmin = 0.0, vmax =20,cmap="YlGnBu", fmt='g')
plt.ylabel('Cohort Month')
plt.xlabel('Cohort Index')
plt.yticks( rotation='360')
plt.show()


# # Conclusion:
# 
# From this cohort analysis of retention rate, we can see the percentage of cohorts that signed in one particular month were 
# active how many months later. here we cn see, in 2017-07 cohort month in 5th index, we see 48.1% which means that 48% of
# cohorts that signed in july 2017 were active 5 months later.
