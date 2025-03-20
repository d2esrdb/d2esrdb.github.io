import shutil
import sys
import typing as t
import re
from pathlib import Path

import click
from mako.lookup import TemplateLookup
from ruamel.yaml import YAML

from db_gen import (
    affixes_generator,
    armor_generator,
    logger,
    recipes_generator,
    runeword_generator,
    set_generator,
    socketables_generator,
    table_strings,
    tables,
    uniques_generator,
    utils,
    weapon_generator,
)

TEMPLATE_DIR = Path(__file__).parent / "templates"
LOOKUP = TemplateLookup(directories=[Path.cwd(), TEMPLATE_DIR])


class DatabaseGenerator:
    def __init__(
        self,
        db_dir: str | Path,
        out_dir: str | Path | None,
        db: dict[str, t.Any],
    ) -> None:
        self.db_dir = Path(db_dir)
        if out_dir:
            self.out_dir = Path(out_dir)
        else:
            self.out_dir = self.db_dir

        self.db_code = db["shortname"]
        self.db_name = db["name"]
        self.db_version = db["version"]
        self.table_strings = table_strings.get_string_dict(
            self.db_dir,
            self.db_code,
            db["tablestring_files"],
        )
        self.mylookup = LOOKUP
        self.tables = tables.Tables(self.db_dir, self.db_code)
        self.utils = utils.Utils(self.tables, self.table_strings)
        self.gemapplytype_names = db["gemapplytype_names"]
        self.to_copy = [s['file'] for s in db.get('extra_static', [])]
        self.extra_static, self.prelinks, self.postlinks = generate_static_links(db)

    def generate(self, body_template: str | bytes, filename: str) -> None:
        base_template = self.mylookup.get_template(uri="base.htm")
        base_rendered = str(
            base_template.render(
                body=body_template,
                name=self.db_name,
                version=self.db_version,
                prelinks=self.prelinks,
                postlinks=self.postlinks,
            ),
        ).replace("\r", "")
        (self.out_dir / self.db_code).mkdir(exist_ok=True)
        (self.out_dir / self.db_code / filename).open("w").write(base_rendered)

    def generate_static(self, extra: list | None, data_dir: Path) -> None:
        if not extra:
            extra = []
        for filename in extra:
            rendered = (data_dir / self.db_code / filename).open().read()
            self.generate(rendered, filename)

    def generate_armor(self) -> None:
        armors = armor_generator.ArmorGenerator(
            self.tables,
            self.table_strings,
            self.utils,
        ).generate_armor()
        armor_template = self.mylookup.get_template(uri="armors.htm")
        armor_rendered = armor_template.render(armors)
        self.generate(armor_rendered, "armors.htm")

    def generate_weapons(self) -> None:
        weapons = weapon_generator.WeaponGenerator(
            self.tables,
            self.table_strings,
            self.utils,
        ).generate_weapons()
        weapon_template = self.mylookup.get_template(uri="weapons.htm")
        weapon_rendered = weapon_template.render(weapons)
        self.generate(weapon_rendered, "weapons.htm")

    def generate_uniques(self) -> None:
        uniques_gen = uniques_generator.UniquesGenerator(
            self.tables,
            self.table_strings,
            self.utils,
        )
        uniques_template = self.mylookup.get_template("uniques.htm")

        unique_weapons = uniques_gen.get_unique_weapons()
        unique_weapon_rendered = uniques_template.render(
            item_groups=unique_weapons,
            page="weapons",
        )
        self.generate(unique_weapon_rendered, "unique_weapons.htm")

        unique_armors = uniques_gen.get_unique_armors()
        unique_armor_rendered = uniques_template.render(
            item_groups=unique_armors,
            page="armors",
        )
        self.generate(unique_armor_rendered, "unique_armors.htm")

        unique_misc = uniques_gen.get_unique_misc()
        unique_misc_rendered = uniques_template.render(
            item_groups=unique_misc,
            page="misc",
        )
        self.generate(unique_misc_rendered, "unique_others.htm")

    def generate_prefixes(self) -> None:
        prefixes = affixes_generator.AffixGenerator(
            self.tables,
            self.table_strings,
            self.utils,
        ).get_prefixes()
        all_types = []
        for prefix in prefixes:
            all_types = all_types + prefix.item_types + prefix.exclude_types
        affix_template = self.mylookup.get_template("affixes.htm")
        affix_rendered = affix_template.render(
            prefixes,
            self.utils.get_item_types_list(list(set(all_types))),
        )
        self.generate(affix_rendered, "prefixes.htm")

    def generate_suffixes(self) -> None:
        suffixes = affixes_generator.AffixGenerator(
            self.tables,
            self.table_strings,
            self.utils,
        ).get_suffixes()
        all_types = []
        for suffix in suffixes:
            all_types = all_types + suffix.item_types + suffix.exclude_types
        affix_template = self.mylookup.get_template("affixes.htm")
        affix_rendered = affix_template.render(
            suffixes,
            self.utils.get_item_types_list(list(set(all_types))),
        )
        self.generate(affix_rendered, "suffixes.htm")

    def remove_html_tags(self, text):
    # Use a regular expression to remove all HTML tags
        clean_text = re.sub(r'<[^>]*>', '', text)
        return clean_text

    def socketable_is_used_in_runeword(self, socketable_code):
        for rw in self.tables.runeword_table:
            for i in range(1,7):
                if rw["Rune" + str(i)] == socketable_code:
                    return True
        return False

    def get_all_used_socketables(self):
        socketables = []
        for socketable in self.tables.socketables_table:
            if socketable["code"] == "":
                continue
            if not self.socketable_is_used_in_runeword(socketable["code"]):
                continue
            socketables.append([self.utils.get_item_name_from_code(socketable["code"]),
                                self.remove_html_tags(self.utils.get_item_name_from_code(socketable["code"]))])
        return socketables

    def get_all_used_runeword_allowed_types(self):
        allowed_bases = set()
        for rw in self.tables.runeword_table:
            for i in range(6):
                if rw["itype" + str(i + 1)] != "":
                    allowed_bases.add(self.utils.get_item_type_name_from_code(rw["itype" + str(i + 1)]))
        return allowed_bases

    def generate_runewords(self) -> None:
        runewords = runeword_generator.RunewordGenerator(
            self.tables,
            self.table_strings,
            self.utils,
        ).generate_runewords()
        filename = "runewords.htm"
        template = self.mylookup.get_template(filename)
        rendered = template.render(runewords, self.gemapplytype_names, self.get_all_used_socketables(), self.get_all_used_runeword_allowed_types())
        self.generate(rendered, filename)

    def generate_socketables(self) -> None:
        socketables = socketables_generator.SocketablesGenerator(
            self.tables,
            self.table_strings,
            self.utils,
        ).generate_socketables()
        filename = "gems.htm"
        template = self.mylookup.get_template(filename)
        rendered = template.render(socketables, self.gemapplytype_names)
        self.generate(rendered, filename)

    def generate_sets(self) -> None:
        sets = set_generator.SetGenerator(self.utils).generate_sets()
        filename = "sets.htm"
        template = self.mylookup.get_template(filename)
        rendered = template.render(sets)
        self.generate(rendered, filename)

    def generate_recipes(self) -> None:
        recipes = recipes_generator.RecipeGenerator(self.utils).generate_recipes()
        filename = "cube.htm"
        template = self.mylookup.get_template(filename)
        rendered = template.render(recipes)
        self.generate(rendered, filename)

    def copy_static(self) ->  None:
        for static in self.to_copy:
            shutil.copy(
                (self.db_dir / self.db_code / static),
                (self.out_dir / self.db_code / static)
            )

    def gen_all(self) -> None:
        self.generate_armor()
        self.generate_weapons()
        self.generate_sets()
        self.generate_runewords()
        self.generate_prefixes()
        self.generate_suffixes()
        self.generate_uniques()
        self.generate_socketables()
        self.generate_recipes()
        self.copy_static()
        self.generate_static(self.extra_static, data_dir=self.db_dir)


def generate_static_links(db: dict[str, t.Any]) -> tuple[list[str], str, str]:
    prelinks = ""
    postlinks = ""
    extra_static = []
    for extra_links in db["extra_pages"]:
        if extra_links["position"] < 0:
            prelinks = prelinks + '<a href="./' + extra_links["file"] + '">[' + extra_links["name"] + "]</a>\n"
            extra_static.append(extra_links["file"])
        if extra_links["position"] > 0:
            postlinks = postlinks + '<a href="./' + extra_links["file"] + '">[' + extra_links["name"] + "]</a>\n"
            extra_static.append(extra_links["file"])
    return extra_static, prelinks, postlinks


def load_config(config_file: Path) -> list[dict[str, t.Any]]:
    yaml = YAML(typ="safe")
    with config_file.open() as config:
        return yaml.load(config)


@click.command()
@click.option("-d", "--db_dir", default="data", type=click.Path(file_okay=False, exists=True, readable=True))
@click.option("-c", "--config", default="data/config.yaml", type=click.Path(file_okay=True, exists=True, readable=True))
@click.option("-o", "--out_dir", default="output", type=click.Path(file_okay=False))
def main(db_dir: str, config: str, out_dir: str) -> None:
    out_path = Path(out_dir)
    out_path.mkdir(exist_ok=True, parents=True)
    db_path = Path(db_dir)

    databases = load_config(Path(config))

    index_links = []

    for db in databases:
        if len(sys.argv) == 1 or sys.argv[1] == db["shortname"]:
            logger.info("----GENERATING " + db["name"] + "-----")

            db_gen = DatabaseGenerator(
                db_path,
                out_path,
                db,
            )
            db_gen.gen_all()

            logger.info("----DONE-----\n")

            index_file = db.get('index', {}).get('file', "armors.htm")
            index_name = db.get('index', {}).get('name', db["name"])
            index_links.append(f'<a href="./{db["shortname"]}/{index_file}">[{index_name}]</a>')

    with (out_path / "index.htm").open("w") as index:
        index.write(str(LOOKUP.get_template("index.htm").render(indexes=index_links)))

    shutil.copyfile("src/db_gen/templates/ads.txt", "output/ads.txt")

if __name__ == "__main__":
    main()
