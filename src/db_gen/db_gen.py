import sys
import typing as t
from pathlib import Path

import click
from mako.lookup import TemplateLookup
from mako.template import Template

from db_gen import (
    affixes_generator,
    armor_generator,
    config,
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


class DatabaseGenerator:
    def __init__(
        self,
        db_dir: str | Path,
        out_dir: str | Path | None,
        db_code: str,
        db_name: str,
        db_version: str,
        string_tables: list[str],
        gemapplytype_names: list[str],
    ) -> None:
        self.db_dir = Path(db_dir)
        if out_dir:
            self.out_dir = Path(out_dir)
        else:
            self.out_dir = self.db_dir
        self.db_code = db_code
        self.db_name = db_name
        self.db_version = db_version
        self.table_strings = table_strings.get_string_dict(
            self.db_dir,
            db_code,
            string_tables,
        )
        self.mylookup = TemplateLookup(directories=[Path.cwd(), TEMPLATE_DIR])
        self.tables = tables.Tables(self.db_dir, db_code)
        self.utils = utils.Utils(self.tables, self.table_strings)
        self.gemapplytype_names = gemapplytype_names

    def generate(self, body_template: str | bytes, filename: str) -> None:
        base_template = self.mylookup.get_template(uri="base.htm")
        base_rendered = str(
            base_template.render(
                body=body_template,
                name=self.db_name,
                version=self.db_version,
            ),
        ).replace("\r", "")
        (self.out_dir / self.db_code).mkdir(exist_ok=True)
        (self.out_dir / self.db_code / filename).open("w").write(base_rendered)

    def generate_static(self, extra: list | None) -> None:
        if not extra:
            extra = []
        filenames = [
            "recipes.htm",
        ]
        filenames = filenames + extra
        for filename in filenames:
            # @TODO delete once we autogen recipes
            if filename in ["recipes.htm"]:
                template = self.mylookup.get_template(filename)
            else:
                template = Template(
                    filename=self.db_code + "/" + filename,
                    lookup=self.mylookup,
                )
            rendered = template.render()
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

    def generate_runewords(self) -> None:
        runewords = runeword_generator.RunewordGenerator(
            self.tables,
            self.table_strings,
            self.utils,
        ).generate_runewords()
        filename = "runewords.htm"
        template = self.mylookup.get_template(filename)
        rendered = template.render(runewords, self.gemapplytype_names)
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


def generate_static_links(db: dict[str, t.Any]) -> list:
    # TODO: don't write to templates dir
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
    prelink_file = (TEMPLATE_DIR / "prelinks.htm").open("w")
    prelink_file.write(prelinks)
    prelink_file.close()
    postlink_file = (TEMPLATE_DIR / "postlinks.htm").open("w")
    postlink_file.write(postlinks)
    postlink_file.close()
    return extra_static


@click.command()
@click.option("--db_dir", default=".")
@click.option("--out_dir", default="output")
def main(db_dir: str, out_dir: str) -> None:
    out_path = Path(out_dir)
    out_path.mkdir(exist_ok=True, parents=True)
    for db in config.databases:
        if len(sys.argv) == 1 or sys.argv[1] == db["shortname"]:
            logger.info("----GENERATING " + db["name"] + "-----")
            extra_static = generate_static_links(db)
            db_gen = DatabaseGenerator(
                Path(db_dir),
                out_path,
                db["shortname"],
                db["name"],
                db["version"],
                db["tablestring_files"],
                db["gemapplytype_names"],
            )
            db_gen.gen_all()
            db_gen.generate_static(extra_static)
            logger.info("----DONE-----\n")
