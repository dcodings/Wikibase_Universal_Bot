"""
author: Diego Chialva
"""

import mygene
from Bio import SeqIO

import pandas as pd

import traceback

import ftplib
import urllib.request

def GeneVirusDataCollector():

    def __init__(self, data_folder, species_names, species_id):
        self.data_frame = None
        self.data_folder = data_folder
        self.species_names = species_names 
        self.species_id = species_id

    def get_data_dataframe(self):
        gene_dataframe = pd.Dataframe(genelist["hits"])
        if csv_output_filepath:
            gene_dataframe.to_csv(csv_output_filepath, index=False)

        return gene_dataframe



    def get_mygene_data(slef,
	                    species, #Comma separated string of names or taxonomy ids.
                        #fields_to_be_returned #List or comma separated string.
                        ):
        label_database = "mygene"
        ## Get list of genes from https://mygene.info/ and create or update items on Wikidats for each annotated gene
        
        try:
            genelist = json.loads(requests.get("https://mygene.info/v3/query?q=*&species="+species).text)
        except requests.exceptions.RequestException as er:  
            raise SystemExit(er)

        print("Returned gene list")
        data_records = []
        for record in genelist["hits"]:
            try:
                geneinfo = json.loads(requests.get("http://mygene.info/v3/gene/"+record["entrezgene"]).text)
                data = {}
                for key in self.data_fields_mapping[label_database]:
                    data.get(key, []).append(geneinfo[key])
                data_records.append(data)
            except requests.exceptions.RequestException as er:  
                print("Could not query for {0}".format(record["entrezgene"]))
                traceback.print_exc()

        return data_records
	
	
	def get_genbank_data(self,
	                 species_id,
                     data_folder_path,
                     features_to_read = ["gene", "CDS"]
                      )
    """
    This downlaod the full file https://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_refseq.txt
    if that is not existing.
    """
    ncbiTaxon = json.loads(requests.get("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=taxonomy&id={}&format=json".format(species_id)).text)

    

    # The tax id to take the refseq from
    wd_item_id_taxon = set_taxon(taxid).wd_item_id
    # assembly_summary_refseq.txt
    # Check if present and if not download file: https://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_refseq.txt .
    if not os.path.isdir(data_folder_path):
        try:
            os.mkdir(data_folder_path)
        except OSError:
            raise OSError("Creation of the directory {} failed".format(data_folder_path))
    file_name = "assembly_summary_refseq.txt"

    assembly_summary_refseq_file_exist = os.path.isfile(os.path.join(os.path(data_folder, file_name)))
    if not assembly_summary_refseq_file_exist:
        url = "https://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_refseq.txt"
        try:
            with urllib.request.urlopen(url) as ur, open(file_name, 'wb') as furl:
                meta = ur.info()
                file_size = int(meta.get_all("Content-Length")[0])
                print("Downloading: {0} Bytes: {1}".format(file_name, file_size))
                furl.write(ur.read())
        except URLError as ue:
            raise URLError("Cannot download assembly_summary_refseq file") from ue

    if assembly_summary_refseq_file_exist:
        with open(os.path.join(os.path(data_folder, "assembly_summary_refseq.txt")), "r") as asrf:
            for line in open("assembly_summary_refseq.txt")):
                line = line.split("\t")
                if len(line) < 10: continue
                # When taxid matches and it is a reference genome download the genbank file from the NCBI
                if line[5] == taxid and line[4] == "reference genome":
                    ftp_full_path + "/" + ftp_line
                    ftp_full_path_list = line[-3].split("/")
                    with ftplib.FTP(ftp_full_path_list[2]) as ftp:
                        ftp.login()
                        ftp.cwd('/' + '/'.join(ftp_full_path.split("/")[3:]))
                        dir_list = []
                        ftp.dir(dir_content.append)
                        for ftp_line in dir_content:
                            if ftp_line.endswith("_genomic.gbff.gz"):
                            ftp_line = ftp_line.split()[-1]
                            genbank_file_full_path = ftp_full_path + "/" + ftp_line
                            try:
                                with urllib.request.urlopen(genbank_file_full_path) as gbur, open(genbank_file_name, 'wb') as gbfile:
                                    meta = gbur.info()
                                    file_size = int(meta.get_all("Content-Length")[0])
                                    print("Downloading: {0} Bytes: {1}".format(ftp_line, file_size))
                                    gbfile.write(gbur.read())
                                except URLError as gbue:
                                    raise URLError("Cannot download {}".format(genbank_file_full_path)) from gbue
                            # Genbank file is compressed, read directly from gzip
                            with open(gbfile, 'rt')as gbfile_read:
                                # Parse as genbank file
                                for seq_record in SeqIO.parse(gbfile_read, "genbank"):
                                    # print(seq_record.id)
                                    # print(repr(seq_record.seq))
                                    # print(len(seq_record))
                                    ## CHECK FROM HERE PLEASE.
                                    data_records = []
                                    for feature in seq_record.features:
                                        # print(feature)
                                        # Match GENE and CDS ?
                                        if feature.type == "gene":
                                            gene_data = {}
                                            gene_data["gene_name"] = #WHAT TO PUT HERE?
                                            
                                            gene_data["NCBI Locus Tag"] = feature.qualifiers.get('locus_tag', [])
                                            gene_data["db_xref"] = feature.qualifiers.get('db_xref', []) # How to model this data in Wikipedia?
                                            strand_orientation = feature.location.strand # Is this guaranteed to alwasy be there as attribute to location? 
                                            gene_data["strand orientation"] = strand_orientation
                                            if strand_orientation == 1:
                                                gene_data["DNA location"] = "Q22809680"
                                            elif strand_orientation == -1:
                                                gene_data["DNA location"] = "Q22809711"
                                            gene_data["Genomic start position"] = str(feature.location.start) # Is this guaranteed to alwasy be there as attribute to location?
                                            gene_data["Genomic end position"] = str(feature.location.end) # Is this guaranteed to alwasy be there as attribute to location?
                                            gene_data["Gene found in taxon"] = wd_item_id_taxon
                                            data_records.append(gene_data)
                                        if feature.type == "CDS":
                                            cds_data = {}
                                            cds_data["CDS found in taxon"] =wd_item_id_taxon
                                            if 'protein_id' in feature.qualifiers:
                                                refseq_protein_ids = feature.qualifiers['protein_id']
                                                # Refseq matching
                                                refseq_regex = "^((AC|AP|NC|NG|NM|NP|NR|NT|NW|XM|XP|XR|YP|ZP)_\d+|(NZ\_[A-Z]{4}\d+))(\.\d+)?$"
                                                pattern = re.compile(refseq_regex)    
                                                for protein_id in refseq_protein_ids:
                                                if pattern.match(protein_id):
                                                    protein_refseq_id = protein_id
                                                    cds_data["CDS RefSeq Protein ID"] = protein_refseq_id
    

    def download_assembly_summary_refseq(self,
                                         data_folder_path,
                                         filename
                                        ):
        if not os.path.isdir(data_folder_path):
            try:
                os.mkdir(data_folder_path)
            except OSError:
                raise OSError("Creation of the directory {} failed".format(data_folder_path))

        url = "https://ftp.ncbi.nlm.nih.gov/genomes/ASSEMBLY_REPORTS/assembly_summary_refseq.txt"
        try:
            with urllib.request.urlopen(url) as ur, open(file_name, 'wb') as furl:
                meta = ur.info()
                file_size = int(meta.get_all("Content-Length")[0])
                print("Downloading: {0} Bytes: {1}".format(file_name, file_size))
                furl.write(ur.read())
        except URLError as ue:
            raise URLError("Cannot download assembly_summary_refseq file") from ue
        return True

