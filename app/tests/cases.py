test_data1 = '/Users/michaelsafdieh/Desktop/basepair/DATA/data1.txt'
# test_data2 = '/Users/michaelsafdieh/Desktop/basepair/DATA/data2.txt'
# test_data3 = '/Users/michaelsafdieh/Desktop/basepair/DATA/data3.txt'
# test_data4 = '/Users/michaelsafdieh/Desktop/basepair/DATA/data4.txt'

sample_cases = [
    {
        'name': '__test_api_sample_1__',
        'genome': 'hg19',
        'datatype': 'rna-seq',
        # 'filepaths1': test_data1,
        # 'filepaths2': '',
        'platform': 'Illumina',
        'default_workflow': 4, # Expression count (STAR) 
        # 'projects': ['/api/v1/projects/3'],
    },
    {
        'name': '__test_api_sample_2__',
        'genome': 'mm10',
        'datatype': 'chip-seq',
        # 'filepaths1': test_data1,
        # 'filepaths2': '',
        'platform': 'Illumina',
        'default_workflow': 4, # Expression count (STAR)
        # 'projects': ['/api/v1/projects/3'],
    }
]
