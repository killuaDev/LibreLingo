import pytest
from unittest.mock import patch, call
import json
import os
import random
from pathlib import Path
from pyfakefs.fake_filesystem_unittest import TestCase as FakeFsTestCase
from . import fakes
from liblili2json.export import export_skill, export_course_skills
from liblili2json.types import Module


def get_fake_skill():
    randomname = str(random.randint(0, 5000))
    return randomname, fakes.customize(
        fakes.skillWithPhraseAndWord,
        name="Animals {}".format(randomname),
    )


class TestExportCourse(FakeFsTestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.export_path = Path("./path{}".format(random.randint(0, 5000)))

    @patch('liblili2json.export.export_skill')
    def test_exports_all_skills(self, export_skill):
        _, fake_skill_1 = get_fake_skill()
        _, fake_skill_2 = get_fake_skill()
        _, fake_skill_3 = get_fake_skill()
        fake_module_1 = Module(title="", skills=[
            fake_skill_1,
            fake_skill_2,
        ])
        fake_module_2 = Module(title="", skills=[
            fake_skill_3,
        ])
        fake_course = fakes.customize(fakes.course1, modules=[
            fake_module_1, fake_module_2
        ])
        export_course_skills(self.export_path, fake_course)
        export_skill.assert_has_calls([
            call(self.export_path, fake_skill_1,  fake_course),
            call(self.export_path, fake_skill_2,  fake_course),
            call(self.export_path, fake_skill_3,  fake_course),
        ], any_order=True)


class TestExportSkill(FakeFsTestCase):
    def setUp(self):
        self.setUpPyfakefs()
        self.export_path = Path("./path{}".format(random.randint(0, 5000)))

    def test_creates_the_correct_file(self):
        randomname, fake_skill = get_fake_skill()
        export_skill(self.export_path,
                     fake_skill, fakes.course1)
        self.assertTrue(os.path.exists(self.export_path / "challenges" /
                                       "animals-{}.json".format(randomname)))

    @patch('liblili2json.export.get_skill_data')
    def test_calls_get_skill_data_with_correct_value(self, get_skill_data):
        get_skill_data.return_value = []
        export_skill(self.export_path,
                     fakes.skillWithPhraseAndWord, fakes.course1)
        get_skill_data.assert_called_with(
            fakes.skillWithPhraseAndWord, fakes.course1)

    @patch('liblili2json.export.get_skill_data')
    def test_writes_correct_value_into_json_file(self, get_skill_data):
        fake_value = {
            "fake_value": random.randint(0, 1000)
        }
        get_skill_data.return_value = fake_value
        export_skill(self.export_path,
                     fakes.skillWithPhraseAndWord, fakes.course1)
        with open(self.export_path /
                  "challenges" / "masculine.json") as f:
            assert json.loads(f.read()) == fake_value

    def test_assert_logs_correctly(self):
        with self.assertLogs("liblili2json", level="INFO") as log:
            randomname = str(random.randint(0, 5000))
            fake_skill = fakes.customize(
                fakes.skillWithPhraseAndWord,
                name="Animals {}".format(randomname),
            )
            export_skill(self.export_path,
                         fake_skill, fakes.course1)
            assert log.output[0] == \
                "INFO:liblili2json:Writing skill '{}'".format(
                fake_skill.name)