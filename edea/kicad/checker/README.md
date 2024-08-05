# Generating the data model

```shell
poetry run datamodel-codegen --url https://gitlab.com/kicad/code/kicad/-/raw/master/resources/schemas/drc.v1.json \
    --output edea/kicad/checker/drc.py \
    --input-file-type jsonschema

poetry run datamodel-codegen --url https://gitlab.com/kicad/code/kicad/-/raw/master/resources/schemas/erc.v1.json \
    --output edea/kicad/checker/erc.py \
    --input-file-type jsonschema
```
