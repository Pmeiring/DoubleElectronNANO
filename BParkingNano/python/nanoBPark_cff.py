from __future__ import print_function
import FWCore.ParameterSet.Config as cms

from PhysicsTools.NanoAOD.common_cff import *
from PhysicsTools.NanoAOD.nano_cff import *
from PhysicsTools.NanoAOD.vertices_cff import *
from PhysicsTools.NanoAOD.NanoAODEDMEventContent_cff import *

from PhysicsTools.NanoAOD.jetsAK4_CHS_cff import *
from PhysicsTools.NanoAOD.jetsAK4_Puppi_cff import *
from PhysicsTools.NanoAOD.jetsAK8_cff import *
from PhysicsTools.NanoAOD.jetMC_cff import *
from PhysicsTools.NanoAOD.muons_cff import *
from PhysicsTools.NanoAOD.taus_cff import *
from PhysicsTools.NanoAOD.boostedTaus_cff import *
from PhysicsTools.NanoAOD.photons_cff import *
from PhysicsTools.NanoAOD.globals_cff import *
from PhysicsTools.NanoAOD.extraflags_cff import *
from PhysicsTools.NanoAOD.ttbarCategorization_cff import *
from PhysicsTools.NanoAOD.genparticles_cff import *
from PhysicsTools.NanoAOD.particlelevel_cff import *
from PhysicsTools.NanoAOD.genWeightsTable_cfi import *
from PhysicsTools.NanoAOD.genVertex_cff import *
from PhysicsTools.NanoAOD.met_cff import *
from PhysicsTools.NanoAOD.triggerObjects_cff import *
from PhysicsTools.NanoAOD.isotracks_cff import *
from PhysicsTools.NanoAOD.protons_cff import *
from PhysicsTools.NanoAOD.fsrPhotons_cff import *
from PhysicsTools.NanoAOD.softActivity_cff import *
from PhysicsTools.NanoAOD.l1trig_cff import *

from DoubleElectronNANO.BParkingNano.trgbits_cff import *

##for gen and trigger muon
from DoubleElectronNANO.BParkingNano.genparticlesBPark_cff import *
from DoubleElectronNANO.BParkingNano.particlelevelBPark_cff import *
from DoubleElectronNANO.BParkingNano.triggerObjectsBPark_cff import *
# from DoubleElectronNANO.BParkingNano.muonsBPark_cff import * 

## filtered input collections
from DoubleElectronNANO.BParkingNano.electronsBPark_cff import * 
from DoubleElectronNANO.BParkingNano.tracksBPark_cff import *

## Dielectron collection
from DoubleElectronNANO.BParkingNano.dielectron_cff import *

# Removing dependency on byVVVLooseDeepTau2018v2p5VSjet, which doesn't work for 2022 preEE mini (v<4) data
finalTaus.cut=cms.string("pt > 18 && ((tauID('decayModeFindingNewDMs') > 0.5 && (tauID('byLooseCombinedIsolationDeltaBetaCorr3Hits') || (tauID('chargedIsoPtSumdR03')+max(0.,tauID('neutralIsoPtSumdR03')-0.072*tauID('puCorrPtSum'))<2.5))) || (?isTauIDAvailable('byUTagCHSVSjetraw')?tauID('byUTagCHSVSjetraw'):-1) > {} || (?isTauIDAvailable('byUTagPUPPIVSjetraw')?tauID('byUTagPUPPIVSjetraw'):-1) > {})".format(0.05, 0.05))

# nanoSequenceOnlyFullSim = cms.Sequence(triggerObjectBParkTables + l1bits)
nanoSequenceOnlyFullSim = cms.Sequence(electronTriggerObjectBParkTables + l1bits)

nanoSequence = cms.Sequence(nanoMetadata + 
                            cms.Sequence(vertexTask) +
                            cms.Sequence(globalTablesTask) + cms.Sequence(vertexTablesTask) +
                            # triggerObjectBParkTables + l1bits)
                            electronTriggerObjectBParkTables + l1bits)

nanoSequenceMC = cms.Sequence(particleLevelBParkSequence + genParticleBParkSequence + 
                              cms.Sequence(globalTablesMCTask) + cms.Sequence(genWeightsTableTask) + genParticleBParkTables + lheInfoTable)

# In privatly produced signal MC, the scale variations were not added
allowedNumScaleWeights.toModify(genWeightsTable, allowedNumScaleWeights = cms.vuint32(0))

nanoSequenceMC_extra = cms.Sequence(cms.Sequence(genParticleTask)
                            + cms.Sequence(particleLevelTask)
                            + cms.Sequence(jetMCTask)
                            + cms.Sequence(muonMCTask)
                            # + cms.Sequence(electronMCTask) # gen-matching for (lowpt/ged) electrons already done
                            # + cms.Sequence(lowPtElectronMCTask)
                            + cms.Sequence(photonMCTask)
                            + cms.Sequence(metMCTable)
                            + cms.Sequence(genVertexTablesTask)
    )

from EgammaUser.EgammaPostRecoTools.EgammaPostRecoTools import setupEgammaPostRecoSeq

def nanoAOD_customizeEgammaPostRecoTools(process):
    setupEgammaPostRecoSeq(process,
                            runEnergyCorrections=False,
                            runVID=True,
                            era='2022-Prompt',
                            eleIDModules=[
                                # Run 3
                                'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_RunIIIWinter22_iso_V1_cff',
                                'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_RunIIIWinter22_noIso_V1_cff',
                                'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Winter22_122X_V1_cff',
                                # Run 2
                                'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_noIso_V2_cff',
                                'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Fall17_iso_V2_cff',
                                'RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Fall17_94X_V2_cff',
                                # # Run 2 BPark retrain
                                # 'DoubleElectronNANO.BParkingNano.mvaElectronID_BParkRetrain_cff',
                                # 'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_BParkRetrain_cff',
                                'DoubleElectronNANO.BParkingNano.mvaElectronID_RunIII_custom_JPsitoEE_cff',
                            ],
                            isMiniAOD=True,
                        )
    return process

from DoubleElectronNANO.BParkingNano.electronsTrigger_cff import *

def nanoAOD_customizeEle(process):
    process.nanoEleSequence = cms.Sequence(
        myUnpackedPatTrigger
        +myPFTriggerMatches
        +myLPTriggerMatches
        +mySlimmedPFElectronsWithEmbeddedTrigger
        +mySlimmedLPElectronsWithEmbeddedTrigger
        +electronTrgSelector
        +hltHighLevel)
    return process

# def nanoAOD_customizeMuonTriggerBPark(process):
#     process.nanoSequence = cms.Sequence( process.nanoSequence + muonBParkSequence + muonBParkTables)#+ muonTriggerMatchedTables)   ###comment in this extra table in case you want to create the TriggerMuon collection again.
#     return process

# def nanoAOD_customizeTrackFilteredBPark(process):
#     process.nanoTracksSequence = cms.Sequence( tracksBParkSequence + tracksBParkTables)
#     return process

def nanoAOD_customizeElectronFilteredBPark(process):
    process.nanoDiEleSequence     = cms.Sequence(electronsBParkSequence + electronBParkTables)
    return process

def nanoAOD_customizeElectronTriggerSelectionBPark(process):
    process.nanoDiEleSequence = cms.Sequence( process.nanoDiEleSequence + electronBParkTriggerSelection)
    return process

def nanoAOD_customizeTriggerBitsBPark(process):
    process.nanoSequence = cms.Sequence( process.nanoSequence + trgTables)
    return process

def nanoAOD_customizeDiElectron(process):
    process.nanoDiEleSequence = cms.Sequence( process.nanoDiEleSequence + DiElectronSequence)
    return process

def nanoAOD_customizeNanoContent(process):
    custom_nanoTableTaskCommon = cms.Task(
        cms.Task(nanoMetadata), 
        jetPuppiTask, jetPuppiForMETTask, jetAK8Task,
        extraFlagsProducersTask, muonTask, tauTask, boostedTauTask,
        electronTask , lowPtElectronTask, photonTask,
        vertexTask, isoTrackTask, jetAK8LepTask,  # must be after all the leptons
        softActivityTask,
        cms.Task(linkedObjects),
        jetPuppiTablesTask, jetAK8TablesTask,
        muonTablesTask, fsrTablesTask, tauTablesTask, boostedTauTablesTask,
        #electronTablesTask, lowPtElectronTablesTask, 
        photonTablesTask,
        globalTablesTask, vertexTablesTask, metTablesTask, extraFlagsTableTask,
        isoTrackTablesTask,softActivityTablesTask
    )

    custom_nanoSequenceCommon = cms.Sequence(custom_nanoTableTaskCommon)

    custom_nanoSequenceOnlyFullSim = cms.Sequence(triggerObjectTablesTask)
    custom_nanoSequenceOnlyData = cms.Sequence(cms.Sequence(protonTablesTask) + lhcInfoTable)

    custom_nanoSequence = cms.Sequence(custom_nanoSequenceCommon + custom_nanoSequenceOnlyData + custom_nanoSequenceOnlyFullSim)
    process.nanoSequence = cms.Sequence( custom_nanoSequence + electronTriggerObjectBParkTables + l1bits )
    return process

from FWCore.ParameterSet.MassReplace import massSearchReplaceAnyInputTag
def nanoAOD_customizeMC(process, saveAllNanoContent=False):
    for name, path in process.paths.iteritems():
        # replace all the non-match embedded inputs with the matched ones
        massSearchReplaceAnyInputTag(path, 'muonTrgSelector:SelectedMuons', 'selectedMuonsMCMatchEmbedded')
        #massSearchReplaceAnyInputTag(path, 'electronTrgSelector:SelectedElectrons', 'selectedElectronsMCMatchEmbedded') # Is this needed if the trigger is emulated ???
        massSearchReplaceAnyInputTag(path, 'electronsForAnalysis:SelectedElectrons', 'selectedElectronsMCMatchEmbedded')
        massSearchReplaceAnyInputTag(path, 'tracksBPark:SelectedTracks', 'tracksBParkMCMatchEmbedded')

        # modify the path to include mc-specific info
        path.insert(0, nanoSequenceMC)
        if saveAllNanoContent: path.insert(0, nanoSequenceMC_extra)
        # path.replace(process.muonBParkSequence, process.muonBParkMC)
        path.replace(process.electronsBParkSequence, process.electronBParkMC)
        path.replace(process.tracksBParkSequence, process.tracksBParkMC)
