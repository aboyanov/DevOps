# Managing User Accounts on Your Linux Instance<a name="managing-users"></a>


Using the default user account is adequate for many applications, but you may choose to add user accounts so that individuals can have their own files and workspaces\. Creating user accounts for new users is much more secure than granting multiple \(possibly inexperienced\) users access to the `ec2-user` account, because that account can cause a lot of damage to a system when used improperly\.

After you add the user account, you must set up access keys that allow the user to log in\.

**Prerequisites**  
Create a key pair for the user or use an existing key pair\.

For example:

```
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

**To add a user account**

1. Use the following adduser command to add the `newuser` account to the system \(with an entry in the `/etc/passwd` file\)\. This command also creates a group and a home directory for the account\.

   ```
   [ec2-user ~]$ sudo adduser alex
   ```

   \[Ubuntu\] When adding a user to an Ubuntu system, include the `--disabled-password` option with this command to avoid adding a password to the account\.

   ```
   [ubuntu ~]$ sudo adduser alex --disabled-password
   ```
   
1. You can optional set a password to a user like that:
   ```
   [ec2-user@ip-172-31-24-113 ~]$ sudo passwd alex
   Changing password for user alex.
   New password:
   Retype new password:
   passwd: all authentication tokens updated successfully.
   ```

1. Switch to the new account so that newly created files have the proper ownership\.

   ```
   [ec2-user ~]$ sudo su - alex
   [alex ~]$
   ```

   Notice that the prompt changes from `ec2-user` to `alex` to indicate that you have switched the shell session to the new account\.

1. Create a `.ssh` directory in the `newuser` home directory and change its file permissions to `700` \(only the owner can read, write, or open the directory\)\.

   ```
   [alex ~]$ mkdir .ssh
   [alex ~]$ chmod 700 .ssh
   ```
**Important**  
Without these exact file permissions, the user will not be able to log in\.

1. Create a file named `authorized_keys` in the `.ssh` directory and change its file permissions to `600` \(only the owner can read or write to the file\)\.

   ```
   [alex ~]$ touch .ssh/authorized_keys
   [alex ~]$ chmod 600 .ssh/authorized_keys
   ```
**Important**  
Without these exact file permissions, the user will not be able to log in\.

1. <a name="edit_auth_keys"></a>Open the `authorized_keys` file using your favorite text editor \(such as **vim** or **nano**\)\.

   ```
   [alex ~]$ vim .ssh/authorized_keys
   ```

   Paste the public key for your key pair into the file and save the changes\. For example:

   ```
   ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQClKsfkNkuSevGj3eYhCe53pcjqP3maAhDFcvBS7O6V
   hz2ItxCih+PnDSUaw+WNQn/mZphTk/a/gU8jEzoOWbkM4yxyb/wB96xbiFveSFJuOp/d6RJhJOI0iBXr
   lsLnBItntckiJ7FbtxJMXLvvwJryDUilBMTjYtwB+QhYXUMOzce5Pjz5/i8SeJtjnV3iAoG/cQk+0FzZ
   qaeJAAHco+CY/5WrUBkrHmFJr6HcXkvJdWPkYQS3xqC0+FmUZofz221CBt5IMucxXPkX4rWi+z7wB3Rb
   BQoQzd8v7yeb7OzlPnWOyN0qFU0XA246RA8QFYiCNYwI3f05p6KLxEXAMPLE
   ```

   The user should now be able to log into the `newuser` account on your instance using the private key that corresponds to the public key that you added to the `authorized_keys` file\.

**To remove a user from the system**  
When you specify the `-r` option, the user's home directory and mail spool are deleted\. To keep the user's home directory and mail spool, omit the `-r` option\.

```
[ec2-user ~]$ sudo userdel -r olduser
```
