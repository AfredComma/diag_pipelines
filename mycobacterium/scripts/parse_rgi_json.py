import json
import mysql.connector

cnx = mysql.connector.connect(option_files=snakemake.input[1], option_groups="myco")
cnx.get_warnings = True
cursor = cnx.cursor()

def parse_rgi_json(filename, curs, log):
    data={}
    with open(filename, "r") as f:
        rgi = json.load(f)
        for j in rgi.keys():
            if j != "_metadata":
                for k in rgi[j].keys():
                    try: 
                        snp=rgi[j][k]["SNP"]
                        try:
                            antibio=rgi[j][k]["ARO_name"].split()[-1]
                            if antibio not in data:
                                data[antibio]={}
                            gene = rgi[j][k]["ARO_name"].split()[2]
                            pos = snp["position"]
                            ref = snp["original"]
                            mut = snp["change"]
                            cmd="INSERT IGNORE INTO mutations (Specimen, software, gene, position, ref_aa, mut_aa) VALUES (\"{0}\", \"rgi\", \"{1}\", {2}, \"{3}\", \"{4}\");".format(str(snakemake.wildcards.sample), gene, pos, ref, mut)
                            curs.execute(cmd)
                            i=curs.fetchwarnings()
                            if i is not None:
                                with open(log, "a") as f:
                                    f.write(i[2]+"\n")
                        except IndexError:
                            pass
                    except KeyError:
                        pass
    return(data)

with open(snakemake.output[0], "w") as myfile:
    myfile.write("")
    
parse_rgi_json(snakemake.input[0], cursor, snakemake.output[0])
cnx.commit()
cnx.close()
