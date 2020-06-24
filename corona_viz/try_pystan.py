
import pystan
import numpy as np
import pandas as pd
# %%

def import_data_col():
    # %
    # os.listdir('/home/teo/_data/covid/world')
    df = pd.read_parquet( '/home/teo/_data/covid/world/df_2020-04-21.parquet')
    df.columns
    df1 = df[ (df['country'] == 'Colombia') & ( df['n_confirmed'].notnull() ) ]
    df1.set_index( "date", inplace=True )
    conf = df1['n_confirmed'].iloc[5:]
    y_raw = conf.diff().fillna(0.0)
    # y[ y == 0 ] = 1
    # %
    y_p1 = y_raw.shift(1, fill_value=0.0)
    y_m1 = y_raw.shift(-1, fill_value=y_raw.iloc[-1])
    # %
    y = ( y_p1 + 2 * y_raw + y_m1) / 4
    y[ y== 0 ] = 1.0

    log_y = np.log(y)[1:]
    # %
    return log_y
    # %%

def normal_model():
    """A simple gaussian model"""
    ocode = """
    data {
        int<lower=1> N;
        real y[N];
    }
    parameters {
        real mu;
    }
    model {
        y ~ normal(mu, 1);
    }
    """
    sm = pystan.StanModel(model_code=ocode)
    y2 = np.random.normal(size=20)
    np.mean(y2)
    # %%
    op = sm.optimizing(data=dict(y=y2, N=len(y2)))
    op
    # %%


def time_series_model():
    """
    L(t) = M / (1 + e^(-b * (t-t1) ))
    L'(t) =  M( 1 + e ... )^(-2) * b e^( -b * (t - t1) )
    log L'(t) = log M - 2 log ( 1 + e ... ) +  log b  + (-b) * (t - t1)

    y_t = mu + err_t
    err_t =  eps_t - phi_1 err_{t-1} - phi_2 err_{t-2}
    """
    # %%

    ocode = """
    functions {
        real logistic(real t, real log_M, real b, real t1 ) {
            return exp(log_M) / ( 1 + exp(-b * (t - t1)) );
        }
        
        real logistic_diff(real t, real log_M, real b, real t1) {
            return exp(log_M) * (   1 / (1 + exp(-b * ( t     - t1))) - 
                                  - 1 / (1 + exp(-b * ( t - 1 - t1))) );   
        }
        
        real log_logistic_diff(real t, real log_M, real b, real t1) {
            return log_M  + log (   1 / (1 + exp(-b * ( t -     t1))) 
                                  - 1 / (1 + exp(-b * ( t - 1 - t1))) );     
        } 
        
    }
    
    data {
        int<lower=1> N;
        real log_y[N];
    }
    
    parameters {
        real t1;
        real log_M;
        real b;
        real sigma; 
        // real phi1;
        // real phi2;
    }
    
    model {
        real err[N];
        real mu1 = log_logistic_diff( 1, log_M, b, t1);
        real mu2 = log_logistic_diff( 2, log_M, b, t1);
        err[1] = log_y[1] - mu1;
        err[2] = log_y[2] - mu2; //  - phi1 * err[1];
            
        for (t in 3:N) {
            real mu;
            mu = log_logistic_diff( t, log_M, b, t1);
            // log_y[t] ~ normal(mu + phi1 * err[t-1] + phi2 * err[t-2], sigma);
            // log_y[t] ~ normal(mu + phi1 * err[t-1], sigma);
            log_y[t] ~ normal( mu, sigma );
            err[t] = log_y[t] - mu; 
        }
        
        t1 ~ exponential( 1.0/  N );
        // phi1 ~ normal(0, 5);
        // phi2 ~ normal(0, 5);
        sigma ~ exponential(1);
        b ~ exponential( 1 );
        log_M ~ exponential( 1/ mean(log_y) );
    }
    """
    ocode_lines = ocode.split("\n")

    sm = pystan.StanModel(model_code=ocode)
    # %%
    log_y = import_data_col()
    # %%
    op = sm.optimizing(data=dict(log_y=log_y, N=log_y.shape[0]))
    # %%
    smps = sm.sampling( data=dict(log_y=log_y.values,
                        N=log_y.shape[0]), warmup=2000, iter=5000 )
    # %%
    smps

# %%
def f(t, t1, log_M, b):
    """logistic growth"""
    return np.exp(log_M) / ( 1 + np.exp( -b * (t-t1) ) )

def f1(t):
    """fixing params"""
    return f( t,  t1=32.21, log_M=8.6, b=0.13 )
# %%


def make_plots( log_y ):
    # %%
    y = np.exp( log_y )
    y_accum = y.cumsum()
    # t = y.index.values - min(y.index.values
    # %
    t_dt = pd.to_datetime( y.index.values )
    t = (t_dt - t_dt.min()).days
    # %%
    pred_accum = f1(t)
    pred = pd.Series( pred_accum, index=y.index).diff()

    df_a = pd.DataFrame( {"t": t, "y_accum": y_accum, "pred_accum": pred_accum} )
    # %%

    df = pd.DataFrame( {"t": t, "y": y, "pred": pred } )
    # %%
    df[['y', 'pred']].plot()
    # %%
    df_a.set_index('t').plot()


# %%
def check_derivative(t):
    # %%
    t1 = 32.74
    log_M = 8.6
    M = np.exp( log_M )
    b = 0.13

    def f1(t_):
        """fixing params"""
        return f(t_, t1=t1, log_M=log_M, b=b)

    d_anal = M * ( 1 + np.exp( -b * ( t - t1 )  ) ) ** (-2) * b * np.exp( -b * (t - t1) )
    log_d_anal = log_M - 2 * log( 1 + exp(-b * (1 - t1)) ) + log(b) - b * (1 - t1);
    d_num = (f1( t + 0.001 ) - f1( t - 0.001) ) / 0.002

    err_deriv = d_anal - d_num
    # %%
    check_df = pd.DataFrame( {'t': t, 'd_num': d_num, 'd_anal': d_anal, 'err': err_deriv } )

    # %%
# %%
