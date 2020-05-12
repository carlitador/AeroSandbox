alt = 0:50:40000;
[T, a, P, rho] = atmoscoesa(alt);


%CREATEFITS(ALT,P,T)
%  Create fits.
%
%  Data for 'pressfit' fit:
%      X Input : alt
%      Y Output: P
%  Data for 'tempfit' fit:
%      X Input : alt
%      Y Output: T
%  Output:
%      fitresult : a cell-array of fit objects representing the fits.
%      gof : structure array with goodness-of fit info.
%
%  See also FIT, CFIT, SFIT.

%  Auto-generated by MATLAB on 08-Nov-2019 12:34:07

%% Initialization.

% Initialize arrays to store fits and goodness-of-fit.
fitresult = cell( 2, 1 );
gof = struct( 'sse', cell( 2, 1 ), ...
    'rsquare', [], 'dfe', [], 'adjrsquare', [], 'rmse', [] );

%% Fit: 'pressfit'.
[xData, yData] = prepareCurveData( alt, P );

% Set up fittype and options.
ft = fittype( 'exp2' );
opts = fitoptions( 'Method', 'NonlinearLeastSquares' );
opts.Display = 'Off';
opts.StartPoint = [144450.53730435 -0.000153087267923548 -41541.5434098163 -0.000216418955828876];

% Fit model to data.
[fitresult{1}, gof(1)] = fit( xData, yData, ft, opts );

% Plot fit with data.
figure( 'Name', 'pressfit' );
h = plot( fitresult{1}, xData, yData );
legend( h, 'P vs. alt', 'pressfit', 'Location', 'NorthEast', 'Interpreter', 'none' );
% Label axes
xlabel( 'alt', 'Interpreter', 'none' );
ylabel( 'P', 'Interpreter', 'none' );
grid on

disp("Pressure");
fitresult{1}
fprintf("a: %.6e\n",fitresult{1}.a);
fprintf("b: %.6e\n",fitresult{1}.b);
fprintf("c: %.6e\n",fitresult{1}.c);
fprintf("d: %.6e\n",fitresult{1}.d);

%% Fit: 'tempfit'.
[xData, yData] = prepareCurveData( alt, T );

% Set up fittype and options.
ft = fittype( 'poly6' );

% Fit model to data.
[fitresult{2}, gof(2)] = fit( xData, yData, ft );

% Plot fit with data.
figure( 'Name', 'tempfit' );
h = plot( fitresult{2}, xData, yData );
legend( h, 'T vs. alt', 'tempfit', 'Location', 'NorthEast', 'Interpreter', 'none' );
% Label axes
xlabel( 'alt', 'Interpreter', 'none' );
ylabel( 'T', 'Interpreter', 'none' );
grid on

disp("Temperature");
fitresult{2}
fprintf("p1: %.6e\n",fitresult{2}.p1);
fprintf("p2: %.6e\n",fitresult{2}.p2);
fprintf("p3: %.6e\n",fitresult{2}.p3);
fprintf("p4: %.6e\n",fitresult{2}.p4);
fprintf("p5: %.6e\n",fitresult{2}.p5);
fprintf("p6: %.6e\n",fitresult{2}.p6);
fprintf("p7: %.6e\n",fitresult{2}.p7);
