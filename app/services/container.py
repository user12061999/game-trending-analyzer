"""Shared service singletons used by the API routers."""

from app.crawlers.orchestrator import CrawlerOrchestrator
from app.analytics.trend_analyzer import TrendAnalyzer
from app.analytics.report_generator import ReportGenerator
from app.analytics.ai_analyst import AIAnalyst
from app.analytics.review_miner import ReviewMiner
from app.analytics.aso_analyzer import ASOAnalyzer
from app.analytics.liveops_tracker import LiveOpsTracker
from app.analytics.creative_spy import CreativeSpy
from app.analytics.cpi_ltv_simulator import CPILTVForecaster
from app.analytics.blue_ocean_finder import BlueOceanFinder
from app.analytics.aso_visual_optimizer import ASOVisualOptimizer
from app.analytics.iap_monetization import IAPMonetizationAnalyzer
from app.analytics.liveops_scheduler import LiveOpsScheduler
from app.analytics.ua_campaign_optimizer import UACampaignOptimizer
from app.analytics.gacha_economy_simulator import GachaEconomySimulator
from app.analytics.publisher_deal_evaluator import PublisherDealEvaluator
from app.analytics.culturalization_scanner import CulturalizationScanner
from app.analytics.churn_chokepoint_analyzer import ChurnChokepointAnalyzer
from app.analytics.viral_kfactor_forecaster import ViralKFactorForecaster
from app.analytics.webhook_bot_service import WebhookBotService
from app.analytics.pitch_deck_generator import PitchDeckGenerator
from app.analytics.ab_testing_calculator import ABTestingCalculator
from app.analytics.ad_mediation_optimizer import AdMediationOptimizer
from app.analytics.playable_ad_generator import PlayableAdGenerator
from app.analytics.voiceover_studio import VoiceoverStudio
from app.analytics.feature_rice_scorer import FeatureRICEScorer
from app.analytics.ad_fraud_scanner import AdFraudScanner
from app.analytics.mmp_webhook_engine import MMPWebhookEngine
from app.crawlers.steam_api_connector import SteamAPIConnector
from app.analytics.gdd_generator import GameDesignDocumentGenerator
from app.analytics.prereg_wishlist_forecaster import PreRegWishlistForecaster
from app.analytics.game_deconstructor import GameDeconstructor
from app.analytics.rea_integrator import REAIntegrator
from app.analytics.revenue_history_engine import RevenueHistoryEngine
from app.analytics.mechanics_hybrid_lab import MechanicsHybridLab
from app.analytics.ad_mediation_engine import AdMediationEngine
from app.notifications.notifier import AlertNotifier
from app.services.crawl_service import CrawlService

orchestrator = CrawlerOrchestrator()
analyzer = TrendAnalyzer()
report_generator = ReportGenerator()
notifier = AlertNotifier()
ai_analyst = AIAnalyst()
review_miner = ReviewMiner()
aso_analyzer = ASOAnalyzer()
liveops_tracker = LiveOpsTracker()
creative_spy = CreativeSpy()
cpi_simulator = CPILTVForecaster()
blue_ocean_finder = BlueOceanFinder()
aso_visual_optimizer = ASOVisualOptimizer()
iap_analyzer = IAPMonetizationAnalyzer()
liveops_scheduler = LiveOpsScheduler()
ua_optimizer = UACampaignOptimizer()
gacha_simulator = GachaEconomySimulator()
publisher_evaluator = PublisherDealEvaluator()
c10n_scanner = CulturalizationScanner()
churn_analyzer = ChurnChokepointAnalyzer()
kfactor_forecaster = ViralKFactorForecaster()
bot_service = WebhookBotService()
pitch_generator = PitchDeckGenerator()
ab_calculator = ABTestingCalculator()
mediation_optimizer = AdMediationOptimizer()
playable_generator = PlayableAdGenerator()
voiceover_studio = VoiceoverStudio()
rice_scorer = FeatureRICEScorer()
ad_fraud_scanner = AdFraudScanner()
mmp_engine = MMPWebhookEngine()
steam_connector = SteamAPIConnector()
gdd_generator = GameDesignDocumentGenerator()
prereg_forecaster = PreRegWishlistForecaster()
game_deconstructor = GameDeconstructor()
rea_integrator = REAIntegrator()
hybrid_lab = MechanicsHybridLab()
ad_mediation_engine = AdMediationEngine()
crawl_service = CrawlService(orchestrator, analyzer, notifier)
