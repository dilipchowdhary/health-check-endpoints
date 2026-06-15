ENV_INDEX=t5
ENV_SERVER=bpm-t5-1.orbpm.ebiz.verizon.com,bpm-t5-2.orbpm.ebiz.verizon.com,bpm-t5-3.orbpm.ebiz.verizon.com,bpm-t5-4.orbpm.ebiz.verizon.com
artifact=bpm-connectedcar:7.2.5
#,bpm-onetalk:7.2.11,bpm-disconnectline:7.2.34,bpm-provision5g:1.3.16,bpm-subscriptionsmanager:1.3.12,
#artifact=bpm-offermanager:1.4.4,bpm-brms:2.2.9,bpm,mlmochangeline:9.3.36,bpm-consumeraddline:7.5.38,bpm-eventnotifier:7.3.57,bpm-customermaintenance:7.3.27
#SERVER=a,b
#artifact=c:1,d:2
IFS=","
#for i in $SERVER
#do
	for j in $artifact
	do
	SERVER=$ENV_SERVER
        ARTIFACT=`echo $j|cut -d ":" -f 1`
        VERSION=`echo $j|cut -d ":" -f 2`
        echo $SERVER,$ARTIFACT,$VERSION
				curl -u dontamu:114c55005b6d5b02af24bcc5550214586f httpssss://jenkins-vcg3.vpc.verizon.com/vcg3/job/VZW.B6VV.ORBPMJobs/job/VZW.B6VV.ORBPM.Deploy.BPM.AWS.DockerCompose.GitPull_NP_NEW/buildWithParameters?token=dontamu_tocken&Environment=$ENV_INDEX&Server=$SERVER&Service_Name=$ARTIFACT_NAME&Service_Version=$VERSION&SyncNode=false&Cluster=C1
	done
#done
