# App imports
from basepair.helpers import eprint

from bin.utils import check_yaml
from bin.common_parser import add_common_args, add_uid_parser, add_json_parser


class Genome:
    
    '''Genome action methods'''

    def get_genome(bp, args):
      '''Get genome'''
      uids=args.uid
      is_json=args.json
      if not uids:
        eprint('At least one uid required.')
        return
      for uid in uids:
        bp.print_data(data_type='genome', uid=uid, is_json=is_json)

    def list_genome(bp, args):
        '''List genomes'''
        bp.print_data(data_type='genomes', is_json=args.json)

    def genome_action_parser(action_parser):
      # get genome parser
      get_genome_p = action_parser.add_parser(
        'get',
        help='List detail info about one or more genomes.'
      )
      get_genome_p = add_common_args(get_genome_p)
      get_genome_p = add_uid_parser(get_genome_p, 'genome')
      get_genome_p = add_json_parser(get_genome_p)

      # list genome parser
      list_genomes_p = action_parser.add_parser(
        'list',
        help='List available genomes.'
      )
      list_genomes_p = add_common_args(list_genomes_p)
      list_genomes_p = add_json_parser(list_genomes_p)

      return action_parser
