// Merges the PF and LowPT collections, sets the isPF and isLowPt 
// UserInt's accordingly

#include "FWCore/Framework/interface/global/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/ConfigurationDescriptions.h"
#include "FWCore/ParameterSet/interface/ParameterSetDescription.h"
#include "FWCore/Utilities/interface/InputTag.h"
#include "DataFormats/Common/interface/View.h"

#include "DataFormats/Candidate/interface/Candidate.h"
#include "DataFormats/PatCandidates/interface/PATObject.h"
#include "DataFormats/PatCandidates/interface/Lepton.h"
#include "DataFormats/PatCandidates/interface/Muon.h"
#include "DataFormats/PatCandidates/interface/Electron.h"

#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "TrackingTools/IPTools/interface/IPTools.h"

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"
#include "DataFormats/EgammaCandidates/interface/Conversion.h"
#include "DataFormats/BeamSpot/interface/BeamSpot.h"
#include "ConversionInfo.h"
#include "CommonTools/Egamma/interface/EffectiveAreas.h"

#include <limits>
#include <algorithm>
#include "helper.h"

class ElectronMerger : public edm::global::EDProducer<> {

  // perhaps we need better structure here (begin run etc)


public:
  bool debug=false; 

  explicit ElectronMerger(const edm::ParameterSet &cfg):
    ttbToken_(esConsumes(edm::ESInputTag{"","TransientTrackBuilder"})),
    triggerLeptons_{ consumes<edm::View<reco::Candidate> >( cfg.getParameter<edm::InputTag>("trgLepton") )},
    triggerBits_{consumes<edm::TriggerResults>(cfg.getParameter<edm::InputTag>("trgBits"))},
    lowpt_src_{consumes<pat::ElectronCollection>( cfg.getParameter<edm::InputTag>("lowptSrc") )},
    pf_src_{ consumes<pat::ElectronCollection>( cfg.getParameter<edm::InputTag>("pfSrc") )},
    rho_pfiso_{ consumes<double>(cfg.getParameter<edm::InputTag>("rho_PFIso")) },
    ea_pfiso_{std::make_unique<EffectiveAreas>((cfg.getParameter<edm::FileInPath>("EAFile_PFIso")).fullPath())},
    pf_mvaId_src_(),
    pf_mvaId_src_Tag_(cfg.getParameter<edm::InputTag>("pfmvaId")),
    pf_mvaId_src_run2_(),
    pf_mvaId_src_Tag_run2_(cfg.getParameter<edm::InputTag>("pfmvaId_Run2")),
    pf_mvaId_src_run3_(),
    pf_mvaId_src_Tag_run3_(cfg.getParameter<edm::InputTag>("pfmvaId_Run3")),
    vertexSrc_{ consumes<reco::VertexCollection> ( cfg.getParameter<edm::InputTag>("vertexCollection") )},
    conversions_{ consumes<edm::View<reco::Conversion> > ( cfg.getParameter<edm::InputTag>("conversions") )},
    beamSpot_{ consumes<reco::BeamSpot> ( cfg.getParameter<edm::InputTag>("beamSpot") )},
    drTrg_cleaning_{cfg.getParameter<double>("drForCleaning_wrtTrgLepton")},
    dzTrg_cleaning_{cfg.getParameter<double>("dzForCleaning_wrtTrgLepton")},
    dr_cleaning_{cfg.getParameter<double>("drForCleaning")},
    dz_cleaning_{cfg.getParameter<double>("dzForCleaning")},
    flagAndclean_{cfg.getParameter<bool>("flagAndclean")},
    pf_ptMin_{cfg.getParameter<double>("pf_ptMin")},
    ptMin_{cfg.getParameter<double>("ptMin")},
    etaMax_{cfg.getParameter<double>("etaMax")},
    bdtMin_{cfg.getParameter<double>("bdtMin")},
    use_gsf_mode_for_p4_{cfg.getParameter<bool>("useGsfModeForP4")},
    use_regression_for_p4_{cfg.getParameter<bool>("useRegressionModeForP4")},
    sortOutputCollections_{cfg.getParameter<bool>("sortOutputCollections")},
    saveLowPtE_{cfg.getParameter<bool>("saveLowPtE")},
    filterEle_{cfg.getParameter<bool>("filterEle")},
    addUserVarsExtra_{cfg.getParameter<bool>("addUserVarsExtra")},
    efficiencyStudy_{cfg.getParameter<bool>("efficiencyStudy")}
    {
      produces<pat::ElectronCollection>("SelectedElectrons");
      produces<TransientTrackCollection>("SelectedTransientElectrons");  
      if ( !pf_mvaId_src_Tag_.label().empty() ) {
        pf_mvaId_src_ = consumes<edm::ValueMap<float> > ( cfg.getParameter<edm::InputTag>("pfmvaId") );
      }
      if ( !pf_mvaId_src_Tag_run2_.label().empty() ) {
        pf_mvaId_src_run2_ = consumes<edm::ValueMap<float> > ( cfg.getParameter<edm::InputTag>("pfmvaId_Run2") );
      }
      if ( !pf_mvaId_src_Tag_run3_.label().empty() ) {
        pf_mvaId_src_run3_ = consumes<edm::ValueMap<float> > ( cfg.getParameter<edm::InputTag>("pfmvaId_Run3") );
    }
    }

  ~ElectronMerger() override {}
  
  void produce(edm::StreamID, edm::Event&, const edm::EventSetup&) const override;

  static void fillDescriptions(edm::ConfigurationDescriptions &descriptions) {}
  
private:
  const edm::ESGetToken<TransientTrackBuilder, TransientTrackRecord> ttbToken_;
  const edm::EDGetTokenT<edm::View<reco::Candidate> > triggerLeptons_;
  const edm::EDGetTokenT<edm::TriggerResults> triggerBits_;
  const edm::EDGetTokenT<pat::ElectronCollection> lowpt_src_;
  const edm::EDGetTokenT<pat::ElectronCollection> pf_src_;
  edm::EDGetTokenT<double> rho_pfiso_;
  std::unique_ptr<EffectiveAreas> ea_pfiso_;
  edm::EDGetTokenT<edm::ValueMap<float>> pf_mvaId_src_;
  const edm::InputTag pf_mvaId_src_Tag_;
  edm::EDGetTokenT<edm::ValueMap<float>> pf_mvaId_src_run2_;
  const edm::InputTag pf_mvaId_src_Tag_run2_;
  edm::EDGetTokenT<edm::ValueMap<float>> pf_mvaId_src_run3_;
  const edm::InputTag pf_mvaId_src_Tag_run3_;
  const edm::EDGetTokenT<reco::VertexCollection> vertexSrc_;
  const edm::EDGetTokenT<edm::View<reco::Conversion> > conversions_;
  const edm::EDGetTokenT<reco::BeamSpot> beamSpot_;
  const double drTrg_cleaning_;
  const double dzTrg_cleaning_;
  const double dr_cleaning_;
  const double dz_cleaning_;
  const bool flagAndclean_;
  const double pf_ptMin_;
  const double ptMin_; //pt min cut
  const double etaMax_; //eta max cut
  const double bdtMin_; //bdt min cut
  const bool use_gsf_mode_for_p4_;
  const bool use_regression_for_p4_;
  const bool sortOutputCollections_;
  const bool saveLowPtE_;
  const bool filterEle_;
  const bool addUserVarsExtra_;
  const bool efficiencyStudy_;

};

void ElectronMerger::produce(edm::StreamID, edm::Event &evt, edm::EventSetup const & iSetup) const {

  //input
  edm::Handle<edm::View<reco::Candidate> > trgLepton;
  evt.getByToken(triggerLeptons_, trgLepton);
  edm::Handle<edm::TriggerResults> triggerBits;
  evt.getByToken(triggerBits_, triggerBits);  
  edm::Handle<pat::ElectronCollection> lowpt;
  if ( saveLowPtE_ ) evt.getByToken(lowpt_src_, lowpt);
  edm::Handle<pat::ElectronCollection> pf;
  evt.getByToken(pf_src_, pf);
  edm::Handle<edm::ValueMap<float> > pfmvaId;  
  if ( !pf_mvaId_src_Tag_.label().empty() ) { evt.getByToken(pf_mvaId_src_, pfmvaId); }
  edm::Handle<edm::ValueMap<float> > pfmvaId_run2;
  if ( !pf_mvaId_src_Tag_run2_.label().empty() ) { evt.getByToken(pf_mvaId_src_run2_, pfmvaId_run2); }
  edm::Handle<edm::ValueMap<float> > pfmvaId_run3;
  if ( !pf_mvaId_src_Tag_run3_.label().empty() ) { evt.getByToken(pf_mvaId_src_run3_, pfmvaId_run3); }

  const auto& theB = iSetup.getData(ttbToken_);
  //
  edm::Handle<reco::VertexCollection> vertexHandle;
  evt.getByToken(vertexSrc_, vertexHandle);
  const reco::Vertex & PV = vertexHandle->front();
  //
  edm::Handle<edm::View<reco::Conversion> > conversions;
  evt.getByToken(conversions_, conversions);
  edm::Handle<reco::BeamSpot> beamSpot;
  evt.getByToken(beamSpot_, beamSpot);
  //
  auto& rho = evt.get(rho_pfiso_);

  // output
  std::unique_ptr<pat::ElectronCollection>  ele_out      (new pat::ElectronCollection );
  std::unique_ptr<TransientTrackCollection> trans_ele_out(new TransientTrackCollection);
  std::vector<std::pair<float, float>> pfEtaPhi;
  std::vector<float> pfVz;
  
  // -> changing order of loops ert Arabella's fix this without need for more vectors  
  size_t ipfele=-1;
  for(auto ele : *pf) {
   ipfele++;

   if (debug) std::cout << "ElectronMerger, Event " << (evt.id()).event() 
			<< " => PF: ele.superCluster()->rawEnergy() = " << ele.superCluster()->rawEnergy()
			<< ", ele.correctedEcalEnergy() = " << ele.correctedEcalEnergy()
			<< ", ele gsf track chi2 = " << ele.gsfTrack()->normalizedChi2()
			<< ", ele.p = " << ele.p() << std::endl;

   //cuts
   bool pTcut = ele.pt()<ptMin_ || ele.pt() < pf_ptMin_;
   bool etaCut = fabs(ele.eta()) > etaMax_;
   
   if(!efficiencyStudy_){
     if(pTcut || etaCut) continue;
   }
   else {
     ele.addUserInt("selection_pTcut", !pTcut); // True if cut is passed -- use as mask
     ele.addUserInt("selection_etaCut", !etaCut);
   }

   // take modes?
   if (use_regression_for_p4_) {
     // pt from regression, eta and phi from gsf track mode
     reco::Candidate::PolarLorentzVector p4(ele.pt(),
					    ele.gsfTrack()->etaMode(),
					    ele.gsfTrack()->phiMode(),
					    ELECTRON_MASS);
     ele.setP4(p4);
   }else if(use_gsf_mode_for_p4_) {
     reco::Candidate::PolarLorentzVector p4(ele.gsfTrack()->ptMode(),
					    ele.gsfTrack()->etaMode(),
					    ele.gsfTrack()->phiMode(),
					    ELECTRON_MASS);
     ele.setP4(p4);
   } else {
     // Fix the mass to the proper one
     reco::Candidate::PolarLorentzVector p4(ele.pt(),
					    ele.eta(),
					    ele.phi(),
					    ELECTRON_MASS);
     ele.setP4(p4);
   }

   // skip electrons inside tag's jet or from different PV
   bool skipEle=true;
   float dzTrg = 0.0;
   for(const auto & trg : *trgLepton) {
     if(reco::deltaR(ele, trg) < drTrg_cleaning_ && drTrg_cleaning_ > 0)
        continue;
     if(fabs(ele.vz() - trg.vz()) > dzTrg_cleaning_ && dzTrg_cleaning_ > 0)
        continue;
     skipEle=false;
     dzTrg = ele.vz() - trg.vz();
     break; // one trg muon to pass is enough :)
   }
   // we skip evts without trg muon
   if (filterEle_ && skipEle) continue;

   // for PF e we set BDT outputs to much higher number than the max
   edm::Ref<pat::ElectronCollection> ref(pf,ipfele);
   float pf_mva_id = 20.;
   if ( !pf_mvaId_src_Tag_.label().empty() ) { pf_mva_id = float((*pfmvaId)[ref]); }
   else pf_mva_id = ele.userFloat("pfmvaId"); // needed for 2022 when manually embedding Run 3 WP; refs to electronMVAValueMapProducer products are not usable here

   float pf_mva_id_run2 = 20.;
   if ( !pf_mvaId_src_Tag_run2_.label().empty() ) { pf_mva_id_run2 = float((*pfmvaId_run2)[ref]); }
   else pf_mva_id_run2 = ele.userFloat("pfmvaId_Run2"); // same as above

   float pf_mva_id_run3 = 20.;
   if ( !pf_mvaId_src_Tag_run3_.label().empty() ) { pf_mva_id_run3 = float((*pfmvaId_run3)[ref]); }
   else pf_mva_id_run3 = ele.userFloat("pfmvaId_Run3"); // same as above

   ele.addUserInt("isPF", 1);
   ele.addUserInt("isLowPt", 0);
   // Custom IDs
   ele.addUserFloat("LPEleSeed_Fall17PtBiasedV1RawValue", 20.); // was called "ptBiased"
   ele.addUserFloat("LPEleSeed_Fall17UnBiasedV1RawValue", 20.); // was called "unBiased"
   ele.addUserFloat("LPEleMvaID_2020Sept15RawValue", 20.); // was called "mvaId"
   ele.addUserFloat("PFEleMvaID_RetrainedRawValue", pf_mva_id); // was called "pfmvaId"
   // Run-2 PF ele ID
   ele.addUserFloat("PFEleMvaID_Fall17NoIsoV2RawValue", pf_mva_id_run2);
   ele.addUserInt("PFEleMvaID_Fall17NoIsoV1wpLoose", ref->electronID("mvaEleID-Fall17-noIso-V1-wpLoose")); //@@ to be deprecated
   ele.addUserInt("PFEleMvaID_Fall17NoIsoV2wpLoose", ref->electronID("mvaEleID-Fall17-noIso-V2-wpLoose"));
   ele.addUserInt("PFEleMvaID_Fall17NoIsoV2wp90", ref->electronID("mvaEleID-Fall17-noIso-V2-wp90"));
   ele.addUserInt("PFEleMvaID_Fall17NoIsoV2wp80", ref->electronID("mvaEleID-Fall17-noIso-V2-wp80"));

   // Run-3 PF ele ID
   ele.addUserFloat("PFEleMvaID_Winter22NoIsoV1RawValue", pf_mva_id_run3);
  //  ele.addUserInt("PFEleMvaID_Winter22NoIsoV1wp90", ref->electronID("mvaEleID-RunIIIWinter22-noIso-V1-wp90"));
  //  ele.addUserInt("PFEleMvaID_Winter22NoIsoV1wp80", ref->electronID("mvaEleID-RunIIIWinter22-noIso-V1-wp80"));
   ele.addUserFloat("chargeMode", ele.charge());
   ele.addUserInt("isPFoverlap", 0);
   ele.addUserFloat("dzTrg", dzTrg);
   ele.addUserInt("skipEle",skipEle);

   // Attempt to match electrons to conversions in "gsfTracksOpenConversions" collection (NO MATCHES EXPECTED)
   ConversionInfo info;
   ConversionInfo::match(beamSpot,conversions,ele,info);
   info.addUserVars(ele);
   if ( addUserVarsExtra_ ) { info.addUserVarsExtra(ele); }

   pfEtaPhi.push_back(std::pair<float, float>(ele.eta(), ele.phi()));
   pfVz.push_back(ele.vz());
   ele_out       -> emplace_back(ele);
  }

  unsigned int pfSelectedSize = pfEtaPhi.size();

  if ( saveLowPtE_ ) {
  size_t iele=-1;
  /// add and clean low pT e
  for(auto ele : *lowpt) {
    iele++;

    if (debug) std::cout << "ElectronMerger, Event " << (evt.id()).event() 
			 << " => LPT: ele.superCluster()->rawEnergy() = " << ele.superCluster()->rawEnergy()
			 << ", ele.correctedEcalEnergy() = " << ele.correctedEcalEnergy()
			 << ", ele gsf track chi2 = " << ele.gsfTrack()->normalizedChi2()
			 << ", ele.p = " << ele.p() << std::endl;
   
   // take modes?
   if (use_regression_for_p4_) {
     // pt from regression, eta and phi from gsf track mode
     reco::Candidate::PolarLorentzVector p4(ele.pt(),
					    ele.gsfTrack()->etaMode(),
					    ele.gsfTrack()->phiMode(),
					    ELECTRON_MASS);
     ele.setP4(p4);
   }else if(use_gsf_mode_for_p4_) {
     reco::Candidate::PolarLorentzVector p4(ele.gsfTrack()->ptMode(),
					    ele.gsfTrack()->etaMode(),
					    ele.gsfTrack()->phiMode(),
					    ELECTRON_MASS);
     ele.setP4(p4);
   } else {
     // Fix the mass to the proper one
     reco::Candidate::PolarLorentzVector p4(ele.pt(),
					    ele.eta(),
					    ele.phi(),
					    ELECTRON_MASS);
     ele.setP4(p4);
   }

   //same cuts as in PF
   bool pTcut = ele.pt() < ptMin_;
   bool etaCut = fabs(ele.eta()) > etaMax_;

   if(!efficiencyStudy_){
     if(pTcut || etaCut) continue;
   }
   else {
     ele.addUserInt("selection_pTcut", !pTcut); // True if cut is passed -- use as mask
     ele.addUserInt("selection_etaCut", !etaCut);
   }

   //assigning BDT values
   float mva_id = ( ele.isElectronIDAvailable("ID") ? ele.electronID("ID") : -100. );
   //  if ( unbiased_seedBDT <bdtMin_) continue; //extra cut for low pT e on BDT
   if ( mva_id < bdtMin_) continue; //extra cut for low pT e on BDT


   bool skipEle=true;
   float dzTrg = 0.0;
   for(const auto & trg : *trgLepton) {
     if(reco::deltaR(ele, trg) < drTrg_cleaning_ && drTrg_cleaning_ > 0)
        continue;
     if(fabs(ele.vz() - trg.vz()) > dzTrg_cleaning_ && dzTrg_cleaning_ > 0)
        continue;
     skipEle=false;
     dzTrg = ele.vz() - trg.vz();
     break;  // one trg muon is enough 
   }
   // same here Do we need evts without trg muon? now we skip them
   if (filterEle_ && skipEle) continue;

   //pf cleaning    
   bool clean_out = false;
   for(unsigned int iEle=0; iEle<pfSelectedSize; ++iEle) {

      clean_out |= (
	           fabs(pfVz[iEle] - ele.vz()) < dz_cleaning_ &&
                   reco::deltaR(ele.eta(), ele.phi(), pfEtaPhi[iEle].first, pfEtaPhi[iEle].second) < dr_cleaning_   );

   }
   if(clean_out && flagAndclean_) continue;
   else if(clean_out) ele.addUserInt("isPFoverlap", 1);
   else ele.addUserInt("isPFoverlap", 0);

   float unbiased_seedBDT = ( ele.isElectronIDAvailable("unbiased") ? ele.electronID("unbiased") : -100. );
   float ptbiased_seedBDT = ( ele.isElectronIDAvailable("ptbiased") ? ele.electronID("ptbiased") : -100. );
   ele.addUserInt("isPF", 0);
   ele.addUserInt("isLowPt", 1);
   // Custom IDs
   ele.addUserFloat("LPEleSeed_Fall17PtBiasedV1RawValue", ptbiased_seedBDT); // was called "ptBiased"
   ele.addUserFloat("LPEleSeed_Fall17UnBiasedV1RawValue", unbiased_seedBDT); // was called "unBiased"
   ele.addUserFloat("LPEleMvaID_2020Sept15RawValue", mva_id); // was called "mvaId"
   ele.addUserFloat("PFEleMvaID_RetrainedRawValue", 20.); // was called "pfmvaId"
   // Run-2 PF ele ID
   ele.addUserFloat("PFEleMvaID_Fall17NoIsoV2RawValue", 20.); // Run 2 ID

   //need to add as placeholders
   ele.addUserInt("PFEleMvaID_Fall17NoIsoV1wpLoose", 0); //@@ to be deprecated
   ele.addUserInt("PFEleMvaID_Fall17NoIsoV2wpLoose", 0);
   ele.addUserInt("PFEleMvaID_Fall17NoIsoV2wp90", 0);
   ele.addUserInt("PFEleMvaID_Fall17NoIsoV2wp80", 0);

   // Run-3 PF ele ID
   ele.addUserFloat("PFEleMvaID_Winter22NoIsoV1RawValue", 20.); // Run 3 ID
   ele.addUserInt("PFEleMvaID_Winter22NoIsoV1wp90", 0); //placeholder
   ele.addUserInt("PFEleMvaID_Winter22NoIsoV1wp80", 0); //placeholder
   ele.addUserFloat("chargeMode", ele.gsfTrack()->chargeMode());
   ele.addUserFloat("dzTrg", dzTrg);
   ele.addUserInt("skipEle",skipEle);

   // Attempt to match electrons to conversions in "gsfTracksOpenConversions" collection
   ConversionInfo info;
   ConversionInfo::match(beamSpot,conversions,ele,info);
   info.addUserVars(ele);
   if ( addUserVarsExtra_ ) { info.addUserVarsExtra(ele); }
   if (debug && info.wpOpen()) { 
     std::cout << "[ElectronMerger::produce]"
	       << " iele: " << iele
	       << ", convOpen: " << (info.wpOpen()?1:0)
	       << ", convLoose: " << (info.wpLoose()?1:0)
	       << ", convTight: " << (info.wpTight()?1:0)
	       << ", convLead: " << int(info.matched_lead.isNonnull()?info.matched_lead.key():-1)
	       << ", convTrail: " << int(info.matched_trail.isNonnull()?info.matched_trail.key():-1)
	       << std::endl;
   }

   ele_out       -> emplace_back(ele);
  }
}

  // Isolation (+ correction)
  size_t ie=-1;
  for(auto &ele : *ele_out){
    ie+=1;
    // Isolation
    auto ea = ea_pfiso_->getEffectiveArea(fabs(ele.superCluster()->eta()));
    float pfisoall0p3 = ele.pfIsolationVariables().sumChargedHadronPt + std::max(0.0, ele.pfIsolationVariables().sumNeutralHadronEt+ele.pfIsolationVariables().sumPhotonEt - rho * ea);
    float pfisoall0p4 = ele.chargedHadronIso() + std::max(0.0, ele.neutralHadronIso() + ele.photonIso() - rho * ea * 16. / 9.);

    // Correction for cases where LowPT electrons don't overlap with PF --> PF reconstructs it as charged hadron --> Need to subtract CTF pt from isolation sum
    float tosub0p3=0.;
    float tosub0p4=0.;

    size_t ilp=-1;
    for(auto &lp : *ele_out){
      ilp+=1;
      if ((lp.userInt("isPF")) || lp.userInt("isPFoverlap")) continue; // skip if lp is known to overlap with PF ele --> no correction needed
      if (!lp.closestCtfTrackRef().isNonnull()) continue;       // skip if lp has no associated CTF track --> no correction possible

      float dR_gsf = reco::deltaR(ele.eta(), ele.phi(), lp.eta(), lp.phi());
      float dR_ctf = reco::deltaR(ele.eta(), ele.phi(), lp.closestCtfTrackRef()->eta(), lp.closestCtfTrackRef()->phi());
      if (dR_gsf<0.001) continue; // skip if lp is same as reference --> cut comes down to numerical precision
      if (dR_ctf < 0.3) tosub0p3+=lp.closestCtfTrackRef()->pt();
      if (dR_ctf < 0.4) tosub0p4+=lp.closestCtfTrackRef()->pt();
    }
    ele.addUserFloat("PFIsoAll03", pfisoall0p3);
    ele.addUserFloat("PFIsoAll03_corr", pfisoall0p3 - tosub0p3);
    ele.addUserFloat("PFIsoChg03_corr", ele.pfIsolationVariables().sumChargedHadronPt - tosub0p3);
    ele.addUserFloat("PFIsoAll04", pfisoall0p4);
    ele.addUserFloat("PFIsoAll04_corr", pfisoall0p4 - tosub0p4);
    ele.addUserFloat("PFIsoChg04_corr", ele.chargedHadronIso() - tosub0p4);
  }

  if(sortOutputCollections_){

    //sorting increases sligtly the time but improves the code efficiency in the Bcandidate builder
    //easier identification of leading and subleading with smarter loop
    std::sort( ele_out->begin(), ele_out->end(), [] (pat::Electron e1, pat::Electron e2) -> bool {return e1.pt() > e2.pt();}
             );
  }

  // TRIGGER MATCHING

  // save useful information related to matched trigger object
  for(auto &ele : *ele_out){
    bool isTriggering = false;
    float drTrg = 999.;
    float dPtOverPtTrg = 999.;
    
    if(ele.triggerObjectMatches().size() != 0){
      isTriggering = true;
      for(auto &trg : ele.triggerObjectMatches()){ //size always 1 since ambiguity resolved
        drTrg = reco::deltaR(ele, trg);
        dPtOverPtTrg = std::abs(ele.pt() - trg.pt())/ele.pt();
      }
    }

    ele.addUserInt("isTriggering", isTriggering);
    ele.addUserFloat("drTrg", drTrg);
    ele.addUserFloat("dPtOverPtTrg", dPtOverPtTrg);
  }

  // build transient track collection
  for(auto &ele : *ele_out){
    float regErrorRatio = std::abs(ele.corrections().combinedP4Error/ele.p()/ele.gsfTrack()->qoverpModeError()*ele.gsfTrack()->qoverpMode());
    const reco::TransientTrack eleTT = use_regression_for_p4_ ?
      theB.buildfromReg(ele.gsfTrack(), math::XYZVector(ele.corrections().combinedP4), regErrorRatio) : theB.buildfromGSF( ele.gsfTrack() );
    trans_ele_out -> emplace_back(eleTT);

    if(ele.userInt("isPF")) continue;
    //compute IP for electrons: need transient track
    //from PhysicsTools/PatAlgos/plugins/LeptonUpdater.cc
    const reco::GsfTrackRef gsfTrk = ele.gsfTrack();
    // PVDZ
    ele.setDB(gsfTrk->dz(PV.position()), std::hypot(gsfTrk->dzError(), PV.zError()), pat::Electron::PVDZ);

    //PV2D
    std::pair<bool, Measurement1D> result = IPTools::signedTransverseImpactParameter(eleTT, GlobalVector(gsfTrk->px(), gsfTrk->py(), gsfTrk->pz()), PV);
    double d0_corr = result.second.value();
    double d0_err = PV.isValid() ? result.second.error() : -1.0;
    ele.setDB(d0_corr, d0_err, pat::Electron::PV2D);

    // PV3D
    result = IPTools::signedImpactParameter3D(eleTT, GlobalVector(gsfTrk->px(), gsfTrk->py(), gsfTrk->pz()), PV);
    d0_corr = result.second.value();
    d0_err = PV.isValid() ? result.second.error() : -1.0;
    ele.setDB(d0_corr, d0_err, pat::Electron::PV3D);
  }
   
  //adding label to be consistent with the muon and track naming
  evt.put(std::move(ele_out),      "SelectedElectrons");
  evt.put(std::move(trans_ele_out),"SelectedTransientElectrons");
}

#include "FWCore/Framework/interface/MakerMacros.h"
DEFINE_FWK_MODULE(ElectronMerger);
