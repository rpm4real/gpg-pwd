# gpg-pwd
A simple password manager built around the GnuPG encryption tool.

## About this project
The goal of this project is to create a simple password manager using the GnuPG (GPG) encryption command line tool. Essentially, the project aims to be a wrapper for a collection of files which contain account and password info, which is continuously decrypted and re-encrypted whenever this info is read/written. 

This project is a work in progress, so please be cautious when using. Currently, the only functioning implementation is found in the v0.5 folder, and should be seen as more of a "proof of concept." Future versions (such as v1.0) look to be more readable, robust, and compact. Potentially these implementations will be in more traditional compiled languages (and more GUI friendly).

The remainder of this readme covers the current functionality of the script within the v0.5 folder. v1.0 is coming soon!

## Dependencies 
- Python 2.x (not yet 3.x compatible)
- GnuPG (https://www.gnupg.org/index.html)

One GPG is installed, one must go through the process of creating a new key, using
```
gpg --gen-key
```

## How to Use
Like most password managers, the key goal is to store many (different) passwords in a system which only requires one master password to access. The system also stores the names of various accounts, as well as "other info," which is intended to be used for any other security credentials relevant to the account. 

The "Initialize Storage File" option must be chosen before any other option can be used. This creates the first record and sets up the manager for future use by creating two JSON files to store all account information. Only one of these files contains actual password information, and only this file goes through the encryption/decryption process for reading/writing. 

In the manager, a "service name" is intended to be named whatever the account is used for (e.g., "Facebook" or "WellsFargo"). The "account name" is the account associated with the service (e.g. "JohnDoe9" or "Johndoe@gmail.com"). Each account name then has a corresponding password. "Other info" is intended to be used for security questions, pin codes, or other information. Lastly, the terms "Global Encryption Passphrase" or simply "encryption passphrase" are used to reference the password associated with the GPG encryption key.

The first service record created when the "Initialize Storage File" option is chosen is named "gpg" and is meant to contain the encryption key account name and passphrase. (This is a useless service, since the password stored is required to obtain the password, but acts as part of the initialization process for the time being.)

The rest of the manager behaves as expected. One should take care to not directly edit any of the JSON files which store the service info (named ```account_base.json``` and ```account_base_secure.json```).

## Known Bugs and Flaws 
- The manager does not correctly handle situations when the encryption passphrase is entered incorrectly--it returns error messages indicating a service doesn't exist even if it does. 
- The "Retrieve a Password" function doesn't correctly handle cases when incorrect information is provided or other errors occur. Use with care.
- The "Initialize Storage File" option may behave unexpectedly when the storage file has already been generated/contains account information. Avoid using unless the storage file has not been initialized. 

Overall, although the manager works, there is much to be fixed and improved upon. Comments and suggestions welcome.
