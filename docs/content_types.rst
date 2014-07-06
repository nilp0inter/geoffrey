Content Types
=============

File
----

``content_type`` **file**

``key`` File real path.

``raw`` File raw content.

Highlight
---------

``content_type``: **highlight**

``key``: File path.

``highlights``: List of highlight elements (see below).

Highlight element
~~~~~~~~~~~~~~~~~

``start_line``: Start line of the highlighting (1-index).

``end_line``: End line of the highlighting.

``start_char``: Start character of the highlighting -relative to `start_line`- (1-index).

``end_char``: End line of the highlighting -relative to `end_line`-.

``text``: Highlight description (short text).

``link``: Relative link to highlight description.

``type``: Highlight type.

Ticket
------

Alert
-----

