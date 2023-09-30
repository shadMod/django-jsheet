# Django JSheet

Django JSheet is a small tool for rendering a simple spreadsheet into a web page.

By taking advantage form_class's fields the cells are set with the appropriate properties^.

There is the ability to use classic excel formulas > see docs for more details

Saving the data is done through an asynchronous method and there is the possibility of a
chronological saving of all changes.

No model is required, but one can possibly be added to allow synchronization of the data with the db.

^(eg IntegerField => int, TypedChoiceField => select etc)

**installation of the django_jsheet_assets package is required)**.

Good luck! \o/