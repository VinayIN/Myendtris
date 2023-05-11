
% trains a model using default chron scheme, prints some statistics

function [model, stats] = trainModel(EEG, approach, targetmarkers, parafolds, paramargin, evalfolds, evalmargin)

% training model
EEG = utl_check_dataset(EEG);
[~, model, stats] = bci_train('Data', EEG, 'Approach', approach, 'TargetMarkers', targetmarkers, 'EvaluationScheme', {'chron', evalfolds, evalmargin}, 'OptimizationScheme', {'chron', parafolds, paramargin});

% reporting statistics
TPs = [];
TNs = [];
ratios = [];
accuracies = [];
fprintf('%s\n', repmat('¯', 1, 63));
for i = 1:length(stats.per_fold)
    TPs = [TPs, stats.per_fold(1,i).TP];
    TNs = [TNs, stats.per_fold(1,i).TN];
    ratios = [ratios, stats.per_fold(1,i).TP / stats.per_fold(1,i).TN];
    accuracies = [accuracies, 1 - stats.per_fold(1,i).mcr];
    fprintf('Fold %2d:   TP %0.3f   TN %0.3f   (Ratio %0.3f)   Accuracy %0.3f\n', i, TPs(i), TNs(i), ratios(i), accuracies(i));
end
fprintf('%s\n', repmat('_', 1, 63));
fprintf('Summary:   TP %0.3f   TN %0.3f   (Ratio %0.3f)   Accuracy %0.3f\n', stats.TP, stats.TN, stats.TP / stats.TN, 1 - stats.mcr);
fprintf('           sd %0.3f   sd %0.3f   (   sd %0.3f)         sd %0.3f\n', std(TPs), std(TNs), std(ratios), std(accuracies));
fprintf('%s\n', repmat('¯', 1, 63));

end