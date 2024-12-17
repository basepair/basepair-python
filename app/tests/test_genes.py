from __future__ import print_function

import unittest

from lib import *
from cases import *

class GeneTest(BaseTest):
    @classmethod
    def setUpClass(cls):
        genome_id = create_fake_genome(cls.bp_super, name='dummy_genome')
        gene_id = create_fake_gene(cls.bp_super, genome_id)
        cls.dummy_data = {
            'gene_id': gene_id,
            'genome_id': genome_id,
        }

    @classmethod
    def tearDownClass(cls):
        cls.bp_super.delete_gene(uid=cls.dummy_data['gene_id'])
        cls.bp_super.delete_genome(uid=cls.dummy_data['genome_id'])
    
    # @unittest.skip('Skipping test_regular_user_can_get_gene')
    def test_regular_user_can_get_gene(self):
        print_test_header('test_regular_user_can_get_gene')
        bp = self.bp
        # genes, code = bp.get_genes_by_info(genome='hg19')
        genes, code = bp.get_genes_by_info(genome='dummy_genome')
        self.assertEqual(code, 200)

        if len(genes) > 0:
            gene_id = genes[0]['id']
            gene = bp.get_gene(uid=gene_id)
            self.assertEqual(gene['id'], gene_id)

        # also test regular get_genes()
        genes = bp.get_genes()
        self.assertGreater(len(genes), 0)

    # @unittest.skip('Skipping test_regular_user_can_get_genome')
    def test_regular_user_can_get_genome(self):
        print_test_header('test_regular_user_can_get_genome')
        bp = self.bp
        genomes = bp.get_genomes()
        self.assertGreater(len(genomes), 0)
        genome_id = genomes[0]['id']
        genome = bp.get_genome(uid=genome_id)
        self.assertEqual(genome['id'], genome_id)

    # @unittest.skip('Skippin test_regular_user_cannot_create_gene')
    def test_regular_user_cannot_create_gene(self):
        bp = self.bp
        bp_super = self.bp_super

        # have super user create a fake genome first
        fake_genome_id = create_fake_genome(bp_super)

        gene_data = {
            'tx_id': 'NM_123',
            'symbol': 'test',
            'chromosome': 'chr12',
            'start_pos': 170234222,
            'end_pos': 170236222,
            'genome': '/api/v1/genomes/' + str(fake_genome_id),
        }
        res = bp.create_gene(data=gene_data)
        self.assertEqual(res.status_code, 401)

        # delete the fake genome
        bp_super.delete_genome(uid=fake_genome_id)

    # @unittest.skip('Skipping test_regular_user_cannot_create_genome')
    def test_regular_user_cannot_create_genome(self):
        print_test_header('test_regular_user_cannot_create_genome')
        bp = self.bp
        genome_data = {
            'name': 'fake_attempt',
        }
        res = bp.create_genome(data=genome_data)
        self.assertEqual(res.status_code, 401)

    # @unittest.skip('Skipping test_regular_user_cannot_update_gene')
    def test_regular_user_cannot_update_gene(self):
        print_test_header('test_regular_user_cannot_update_gene')
        bp = self.bp
        bp_super = self.bp_super

        # have super user create a fake genome and gene first
        fake_genome_id = create_fake_genome(bp_super)
        fake_gene_id = create_fake_gene(bp_super, fake_genome_id)

        gene_update_data = {
            'symbol': 'test_update_attempt',
        }
        res = bp.update_gene(uid=fake_gene_id, data=gene_update_data)
        self.assertEqual(res.status_code, 401)

        # delete the fake genome and gene
        bp_super.delete_gene(uid=fake_gene_id)
        bp_super.delete_genome(uid=fake_genome_id)

    # @unittest.skip('Skipping test_regular_user_cannot_update_genome')
    def test_regular_user_cannot_update_genome(self):
        print_test_header('test_regular_user_cannot_update_genome')
        bp = self.bp
        bp_super = self.bp_super

        # have super user create a fake genome first
        fake_genome_id = create_fake_genome(bp_super)

        genome_update_data = {
            'name': 'fake_update_attempt',
        }
        res = bp.update_genome(uid=fake_genome_id, data=genome_update_data)
        self.assertEqual(res.status_code, 401)

        # delete the fake genome
        bp_super.delete_genome(uid=fake_genome_id)

    # @unittest.skip('Skipping test_regular_user_cannot_delete_gene')
    def test_regular_user_cannot_delete_gene(self):
        print_test_header('test_regular_user_cannot_delete_gene')
        bp = self.bp
        bp_super = self.bp_super

        # have super user create a fake genome and gene first
        fake_genome_id = create_fake_genome(bp_super)
        fake_gene_id = create_fake_gene(bp_super, fake_genome_id)

        res = bp.delete_gene(uid=fake_gene_id)
        self.assertEqual(res.status_code, 401)

        # delete the fake genome and gene
        bp_super.delete_gene(uid=fake_gene_id)
        bp_super.delete_genome(uid=fake_genome_id)

    # @unittest.skip('Skipping test_regular_user_cannot_delete_genome')
    def test_regular_user_cannot_delete_genome(self):
        print_test_header('test_regular_user_cannot_delete_genome')
        bp = self.bp
        bp_super = self.bp_super

        # have super user create a fake genome first
        fake_genome_id = create_fake_genome(bp_super)

        res = bp.delete_genome(uid=fake_genome_id)
        self.assertEqual(res.status_code, 401)

        # delete the fake genome
        bp_super.delete_genome(uid=fake_genome_id)


    # @unittest.skip('Skipping test_super_user_can_get_gene')
    def test_super_user_can_get_gene(self):
        print_test_header('test_super_user_can_get_gene')
        bp_super = self.bp_super
        # genes, code = bp_super.get_genes_by_info(genome='hg19')
        genes, code = bp_super.get_genes_by_info(genome='dummy_genome')
        self.assertEqual(code, 200)

        if len(genes) > 0:
            gene_id = genes[0]['id']
            gene = bp_super.get_gene(uid=gene_id)
            self.assertEqual(gene['id'], gene_id)

        # also test regular get_genes()
        genes = bp_super.get_genes()
        self.assertGreater(len(genes), 0)

    # @unittest.skip('Skipping test_super_user_can_get_genome')
    def test_super_user_can_get_genome(self):
        print_test_header('test_super_user_can_get_genome')
        bp_super = self.bp_super
        genomes = bp_super.get_genomes()
        self.assertGreater(len(genomes), 0)

        genome_id = genomes[0]['id']
        genome = bp_super.get_genome(uid=genome_id)
        self.assertEqual(genome['id'], genome_id)

    # @unittest.skip('Skipping test_super_user_can_create_gene')
    def test_super_user_can_create_gene(self):
        print_test_header('test_super_user_can_create_gene')
        bp_super = self.bp_super
        fake_genome_id = create_fake_genome(bp_super)

        gene_data = {
            'tx_id': 'NM_123',
            'symbol': 'test',
            'chromosome': 'chr12',
            'start_pos': 170234222,
            'end_pos': 170236222,
            'genome': '/api/v1/genomes/' + str(fake_genome_id),
        }
        res = bp_super.create_gene(data=gene_data)
        gene_id = bp_super.parse_url(res.headers['location'])['id']
        gene = bp_super.get_gene(uid=gene_id)
        self.assertEqual(str(gene['id']), str(gene_id))
        compare_info(gene_data, gene)

        # delete the fake genome and created gene
        bp_super.delete_gene(uid=gene_id)
        bp_super.delete_genome(uid=fake_genome_id)

    # @unittest.skip('Skipping test_super_user_can_create_genome')
    def test_super_user_can_create_genome(self):
        print_test_header('test_super_user_can_create_genome')
        bp_super = self.bp_super

        genome_data = {
            'name': 'fake',
        }
        res = bp_super.create_genome(data=genome_data)
        genome_id = bp_super.parse_url(res.headers['location'])['id']
        genome = bp_super.get_genome(uid=genome_id)
        self.assertEqual(str(genome['id']), str(genome_id))
        compare_info(genome_data, genome)

        # delete the created genome
        bp_super.delete_genome(uid=genome_id)

    # @unittest.skip('Skipping test_super_user_can_update_gene')
    def test_super_user_can_update_gene(self):
        print_test_header('test_super_user_can_update_gene')
        bp_super = self.bp_super
        fake_genome_id = create_fake_genome(bp_super)
        fake_gene_id = create_fake_gene(bp_super, fake_genome_id)

        gene_update_data = {
            'symbol': 'test_update',
        }
        res = bp_super.update_gene(uid=fake_gene_id, data=gene_update_data)
        self.assertEqual(res.status_code, 204)
        gene = bp_super.get_gene(uid=fake_gene_id)
        self.assertEqual(str(gene['id']), str(fake_gene_id))
        compare_info(gene_update_data, gene)

        # delete the fake genome and gene
        bp_super.delete_gene(uid=fake_gene_id)
        bp_super.delete_genome(uid=fake_genome_id)

    # @unittest.skip('Skipping test_super_user_can_update_genome')
    def test_super_user_can_update_genome(self):
        print_test_header('test_super_user_can_update_genome')
        bp_super = self.bp_super
        fake_genome_id = create_fake_genome(bp_super)

        genome_update_data = {
            'name': 'fake_update',
        }
        res = bp_super.update_genome(uid=fake_genome_id, data=genome_update_data)
        self.assertEqual(res.status_code, 204)
        genome = bp_super.get_genome(uid=fake_genome_id)
        self.assertEqual(str(genome['id']), str(fake_genome_id))
        compare_info(genome_update_data, genome)

        # delete the fake genome
        bp_super.delete_genome(uid=fake_genome_id)

    # @unittest.skip('Skipping test_super_user_can_delete_gene')
    def test_super_user_can_delete_gene(self):
        print_test_header('test_super_user_can_delete_gene')
        bp_super = self.bp_super
        fake_genome_id = create_fake_genome(bp_super)
        fake_gene_id = create_fake_gene(bp_super, fake_genome_id)

        res = bp_super.delete_gene(uid=fake_gene_id)
        self.assertEqual(res.status_code, 204)

        bp_super.delete_genome(uid=fake_genome_id)

    # @unittest.skip('Skipping test_super_user_can_delete_genome')
    def test_super_user_can_delete_genome(self):
        print_test_header('test_super_user_can_delete_genome')
        bp_super = self.bp_super
        fake_genome_id = create_fake_genome(bp_super)

        res = bp_super.delete_genome(uid=fake_genome_id)
        self.assertEqual(res.status_code, 204)

def create_fake_genome(bp, name='fake'):
    genome_data = {
        'name': name,
    }
    res = bp.create_genome(data=genome_data)
    return bp.parse_url(res.headers['location'])['id']

def create_fake_gene(bp, genome_id):
    gene_data = {
        'tx_id': 'NM_123',
        'symbol': 'test',
        'chromosome': 'chr12',
        'start_pos': 170234222,
        'end_pos': 170236222,
        'genome': '/api/v1/genomes/' + str(genome_id),
    }
    res = bp.create_gene(data=gene_data)
    return bp.parse_url(res.headers['location'])['id']

def print_test_header(msg):
    # print('\n##### API: {} #####\n'.format(msg), file=sys.stderr)
    print('\nsharing_api>>> {}\n'.format(msg),file=sys.stderr)


if __name__ == '__main__':
    unittest.main()