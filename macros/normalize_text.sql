{% macro normalize_text(column_name) -%}
    regexp_replace(
        upper(strip_accents(trim(cast({{ column_name }} as varchar)))),
        '\\s+',
        ' ',
        'g'
    )
{%- endmacro %}

