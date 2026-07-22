from django.apps import apps


def get_database_schema():

    schema = []

    for model in apps.get_models():

        schema.append(f"Table: {model._meta.db_table}")

        for field in model._meta.fields:

            line = f"{field.name} ({field.get_internal_type()})"

            if field.is_relation:

                line += f" -> {field.related_model._meta.db_table}"

            schema.append(line)

        schema.append("")

    return "\n".join(schema)