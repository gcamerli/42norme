# **42norme**

42 (Paris)

### **Description**

**42norme** is a python implementation of the official 42 **norminette**.

### **Requirements**

+ python
+ pika (pip)

### **Usage**

Just run:

```bash
python norminette.py
```

For a better configuration export the PATH of this folder inside
your `.zshrc` and set an alias like this:

`alias norm="python $NORM/norminette.py"`

To see the help add the flags `--help`.

### **Notes**

+ It's possible to use it just connecting to **42** wifi.

+ It's necessary to set properly the [kerberos](https://github.com/gcamerli/42krb) access to execute it (**42norme** directly connects to the official `norminette.42.fr` to display the results).

+ It's not possible to use the flag:

`CheckForbiddenSourceHeader`

### **Credits**

+ [@lefta](https://github.com/lefta)

### **GPL License**

This work is licensed under the terms of **[GNU General Public License v3.0](https://www.gnu.org/licenses/gpl.html)**.
