library(DoE.base)
for(i in 2:9){
		x<-seq(1,i)
		filename = sprintf("./OA.V1.L%d.tbl",i)
		write.table(x,file=filename,sep=" ",col.names=FALSE,row.names=FALSE,quote=FALSE)
}
for(i in 2:10){
	for(j in 2:9){
		x<-oa.design(nfactors=i,nlevels=j)
		filename = sprintf("./OA.V%d.L%d.tbl",i,j)
		write.table(x,file=filename,sep=" ",col.names=FALSE,row.names=FALSE,quote=FALSE)
	}
}

for(i in 11:40){
	x<-oa.design(nfactors=i,nlevels=2)
  filename = sprintf("./OA.V%d.L%d.tbl",i,2)
	write.table(x,file=filename,sep=" ",col.names=FALSE,row.names=FALSE,quote=FALSE)
	}
