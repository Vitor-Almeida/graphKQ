from allennlp.predictors.predictor import Predictor
import allennlp_models.tagging

predictor = Predictor.from_path("/home/jaco/Projetos/graphKQ/data/pretrainedmodels/structured-prediction-srl-bert.2020.12.15.tar.gz")
print(predictor.predict(sentence="Did Uriah honestly think he could beat the game in under three hours?."))