# ItemCatalog
> Majd Saleh

The Item Catalog project consists of developing an application that provides a list of items within a variety of categories, as well as provide a user registration and authentication system. This project uses persistent data storage to create a RESTful web application that allows users to perform Create, Read, Update, and Delete operations.

## Prerequisites
- Unix-Style Terminal Program
- [Vagrant](https://www.vagrantup.com/downloads.html).
- [VirtualBox](https://www.virtualbox.org/wiki/Downloads).
- [FSND Virtual Machine](https://github.com/udacity/fullstack-nanodegree-vm).

## Getting Started
1. Install Vagrant and VirtualBox.
2. Clone the Vagrantfile from the Udacity Repo.
3. Clone this repo into the catlog/ directory found in the Vagrant directory.
4. Run vagrant up to run the virtual machine, then vagrant ssh to login to the VM.
5. Change directory to the catalog project directory.
```
vagrant up
vagrant ssh
cd /vagrant/catalog

```
6. Setup the database using `python database_setup.py`.
7. Fill the database using `python seeder.py`.
8. Run the server using `python Application.py`.
9. Open your browser and go to http://localhost/categories to access the application.

## Login 
This program uses third-party auth with Google , to login just press the button at the top of the page from the right. 

>note: A user does not need to be logged in in order to read the categories or items uploaded. However, users who created an item are the only users allowed to update or delete the item that they created.

## JSON Endpoints
- To get a list of all Categories and their items --> `/catalog/JSON`
- To get a list of all Items in the particular category -->  `/catalog/<string:category_name>/JSON`
- To get Items `/catalog/<string:category>/<int:item_id>/JSON`

## Technologies Used 
- Flask.
- Bootsrap,.
- SQLAchemy.
- OAuth.
