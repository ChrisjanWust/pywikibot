# -*- coding: utf-8 -*-
"""Test generate_family_files script."""
#
# (C) Pywikibot team, 2018-2020
#
# Distributed under the terms of the MIT license.
#
from __future__ import absolute_import, division, unicode_literals

from random import sample

from pywikibot import Site
from pywikibot.tools import PY2

from tests.aspects import unittest, DefaultSiteTestCase

import generate_family_file

if not PY2:
    from urllib.parse import urlparse
else:
    from urlparse import urlparse


class FamilyTestGenerator(generate_family_file.FamilyFileGenerator):

    """Family file test creator."""

    def getapis(self):
        """Only load additional ten additional different wikis randomly."""
        save = self.langs
        self.langs = sample(save, 10)
        self.prefixes = [item['prefix'] for item in self.langs]
        super(FamilyTestGenerator, self).getapis()
        self.langs = save

    def writefile(self):
        """Pass writing."""
        pass


class TestGenerateFamilyFiles(DefaultSiteTestCase):

    """Test generate_family_file functionality."""

    familyname = 'testgff'

    def setUp(self):
        """Set up tests class."""
        super(TestGenerateFamilyFiles, self).setUp()
        self.generator_instance = FamilyTestGenerator(
            url=self.site.base_url(''), name=self.familyname, dointerwiki='y')

    def test_initial_attributes(self):
        """Test initial FamilyFileGenerator attributes."""
        self.assertEqual(self.generator_instance.base_url,
                         self.site.base_url(''))
        self.assertEqual(self.generator_instance.name, self.familyname)
        self.assertEqual(self.generator_instance.dointerwiki, 'y')
        self.assertIsInstance(self.generator_instance.wikis, dict)
        self.assertIsInstance(self.generator_instance.langs, list)

    def test_attributes_after_run(self):
        """Test FamilyFileGenerator attributes after run()."""
        gen = self.generator_instance
        gen.run()

        with self.subTest(test='Test whether default is loaded'):
            self.assertIn(self.site.lang, gen.wikis)

        with self.subTest(test='Test element counts'):
            if self.site.lang not in gen.prefixes:
                gen.prefixes += [self.site.lang]
            self.assertCountEqual(gen.prefixes, gen.wikis)

        # test creating Site from url
        # only test Sites for downloaded wikis (T241413)
        for language in filter(lambda x: x['prefix'] in gen.wikis, gen.langs):
            lang = language['prefix']
            url = language['url']
            wiki = gen.wikis[lang]
            lang_parse = urlparse(url)
            wiki_parse = urlparse(wiki.server)

            with self.subTest(url=url):
                if lang_parse.netloc != wiki_parse.netloc:
                    # skip redirected url (T241413)
                    self.skipTest(
                        '{} is redirected to {}'
                        .format(lang_parse.netloc, wiki_parse.netloc))

                site = Site(url=url)

                try:  # T194138 to be solved
                    self.assertEqual(site.lang, lang,
                                     'url has lang "{lang}" '
                                     'but Site {site} has lang "{site.lang}"'
                                     .format(site=site, lang=lang))
                except AssertionError:
                    self.skipTest('KNOWN BUG: url has lang "{lang}" '
                                  'but Site {site} has lang "{site.lang}"'
                                  .format(site=site, lang=lang))


if __name__ == '__main__':  # pragma: no cover
    try:
        unittest.main()
    except SystemExit:
        pass
