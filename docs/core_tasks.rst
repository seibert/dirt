Core tasks API
==============

dirt itself contains a minimum of "core" tasks -- only those needed to set up the remote execution environment. More interesting tasks are implemented in derivative projects.

dirt.tasks.system_info
----------------------
Returns useful system information from os, sys, and socket.

.. automodule:: dirt.tasks.system_info
   :members:

dirt.tasks.ping
---------------
A special task that does not return a dictionary, only a boolean. Used internally by dirt to confirm a node is accepting connections before sending it a task.

.. automodule:: dirt.tasks.ping
   :members:

