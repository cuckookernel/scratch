package main


func DNAStrand(dna string) string {
	var out [] byte;
	bmap := map[byte] byte { 'A': 'T', 'T': 'A', 'G':'C', 'C': 'G' }

	for i:=0; i < len(dna); i++ {
	  out1 := bmap[dna[i]]
	  out = append(out, out1)
	}

	return string(out)
 }
