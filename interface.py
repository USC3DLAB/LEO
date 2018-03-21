import sys
import os
import csv
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats
from PyQt5.QtWebEngineWidgets import QWebEngineView # pylint: disable=E0611
from PyQt5.QtCore import QUrl # pylint: disable=E0611
from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QApplication, QWidget, QDesktopWidget, QFileDialog # pylint: disable=E0611
# pylint: disable-msg=E0611

class LEO(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()
        self.statusBar()
        self.compared_data = []
        self.compared_data_type = None
        self.test_data = []
        self.ERROR_term  = []
        self.test_data_type = None
        self.save_folder = './'
        self.log_file_name = ''
        self.pysp_file = None
        self.f = None
        self.tpye = None
        self.SL_Data = None
        


        self.browser = QWebEngineView()
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "intro.html"))
        local_url = QUrl.fromLocalFile(file_path)
        self.browser.load(local_url)
        self.setCentralWidget(self.browser)

    def initUI(self):

        # set window's size and position
        self.resize(1000, 800)
        self.center()

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        fileMenu = menubar.addMenu('File')
        ##impMenu = QMenu('Import', self)
        # impAct = QAction('Import data file', self)
        ##impMenu.addAction(impAct)

        newAct = QAction('Generate log data', self)
        newAct.setStatusTip('Generate a text file, which will contains all the output information from this software')
        newAct.triggered.connect(self.generate_log_file)
        fileMenu.addAction(newAct)
        # fileMenu.addMenu(impMenu)

        SLMenu = menubar.addMenu('SL data')
        SL_data_load = QAction('Load SL data(*.csv)', self)
        SL_data_load.triggered.connect(self.SL_data_load)
        SLMenu.addAction(SL_data_load)

        ERROR_term_load = QAction('Load the test error terms and validation error terms data(*.csv)', self)
        ERROR_term_load.triggered.connect(self.ERROR_term_load)
        SLMenu.addAction(ERROR_term_load)

        CHI_for_error = QAction('perform a χ2-test for error termspy', self)
        CHI_for_error.triggered.connect(self.CHI_for_error)
        SLMenu.addAction(CHI_for_error)


        SPMenu = menubar.addMenu('SP Model')
        PySP = QAction('Load SP model(*.py) and use PySP', self)
        PySP.setStatusTip('Choose your SP model in *.py type, which will be used with PySP to generate SMPS files')
        PySP.triggered.connect(self.PySP)
        SPMenu.addAction(PySP)

        SMPS = QAction('Choose the SMPS folder', self)
        SMPS.setStatusTip('Choose your SP model in *.py type, which will be used with PySP to generate SMPS files')
        SMPS.triggered.connect(self.SMPS)
        SPMenu.addAction(SMPS)

        SD = QAction('Load SP model(*.py) and use PySP', self)
        SD.setStatusTip('Use SD solver to ')
        SD.triggered.connect(self.SD)
        SPMenu.addAction(SD)


        """"
        StatiticalmodelMenu = menubar.addMenu('Predictive Models')
        timeseries = QAction('Time Series', self)
        StatiticalmodelMenu.addAction(timeseries)
        lr = QAction('Linear Regression', self)
        StatiticalmodelMenu.addAction(lr)

        SOMenu = menubar.addMenu('Prescriptive Models')
        lp = QAction('Linear Programming', self)
        SOMenu.addAction(lp)
        sdndu = QAction('Stochastic Decomposition(Normally Distributed and Uncorrelated)', self)
        SOMenu.addAction(sdndu)
        sdndc = QAction('Stochastic Decomposition(Normally Distributed and Correlated)', self)
        SOMenu.addAction(sdndc)
        sdeae = QAction('Stochastic Decomposition(Empirical Additive Errors)', self)
        SOMenu.addAction(sdeae)
        saa = QAction('Sampling Average Approximation(Empirical Additive Errors)', self)
        SOMenu.addAction(saa)

        dataMenu = menubar.addMenu('Data')
        outputdata = QAction('Load output data', self)
        dataMenu.addAction(outputdata)
        """

        testMenu = menubar.addMenu('Model Validation')

        ## data for validation
        data_validation = QAction('*Choose data file for validation', self)
        data_validation.setStatusTip('Choose the train data file and validation data file(*.csv) in order for test')
        data_validation.triggered.connect(self.open_file)
        testMenu.addAction(data_validation)

        chi = QAction('Chi-square test for error terms and cost-to-go objectives', self)
        chi.triggered.connect(self.chisquaredtest)

        testMenu.addAction(chi)
        ttest = QAction('T-test for the mean of cost-to-go function', self)
        ttest.triggered.connect(self.ttest)
        testMenu.addAction(ttest)
        ftest = QAction('F-test for the variance of cost-to-go function', self)
        ftest.triggered.connect(self.ftest)
        testMenu.addAction(ftest)
        outliers = QAction('Tests to identify outliers', self)
        testMenu.addAction(outliers)
        prediction = QAction('Prediction and confidence intervals', self)
        testMenu.addAction(prediction)

        # Compare data performance
        ComparationMenu = menubar.addMenu('Compare')

        data_folder = QAction('*Compare data', self)
        data_folder.setStatusTip('Choose all the validation data files for compare')
        data_folder.triggered.connect(self.open_compared_file)
        ComparationMenu.addAction(data_folder)

        kwtest = QAction('Kruskal-Wallis test', self)
        kwtest.triggered.connect(self.kwtest)
        ComparationMenu.addAction(kwtest)
        cdf = QAction('CDF', self)
        cdf.triggered.connect(self.cdf)
        ComparationMenu.addAction(cdf)


        helpMenu = menubar.addMenu('Help')
        helpdoc = QAction('Documents', self)
        helpMenu.addAction(helpdoc)
        examples = QAction('Examples', self)
        helpMenu.addAction(examples)


        self.setWindowTitle('Learning Enabled Optimization')
        self.show()


    def PySP(self):
        self.pysp_file, self.type = QFileDialog.getOpenFileName(self,
                                                            "Choose one SL data(*.csv)",
                                                            "./",
                                                            "Python Files (*.py);;Python Files (*.py)")  ## open file, set file type filter
        self.f = open(self.log_file_name,'a')
        print('Load the following file for PySP to generate SMPS files:\n' + self.pysp_file + '\n')
        self.f.write('Load the following file for PySP to generate SMPS files:\n')
        self.f.write(self.pysp_file + '\n')
        self.f.close()

    



    def SMPS(self):
        return

    def SD(self):
        return


    def SL_data_load(self):
        self.SL_Data, self.type = QFileDialog.getOpenFileName(self,
                                                            "Choose one SL data(*.csv)",
                                                            "./",
                                                            "CSV Files (*.CSV);;CSV Files (*.csv)")  ## open file, set file type filter
        self.f = open(self.log_file_name,'a')
        print('Load the following SL data:\n' + self.SL_Data + '\n')
        self.f.write('Load the following SL data:\n')
        self.f.write(self.SL_Data + '\n')
        self.f.close()

    def ERROR_term_load(self):
        self.ERROR_term, self.type = QFileDialog.getOpenFileNames(self,
                                                            "Choose two error terms data files(*.csv)",
                                                            "./",
                                                            "CSV Files (*.CSV);;CSV Files (*.csv)")  ## open file, set file type filter
        self.f = open(self.log_file_name,'a')
        print('Load the following error terms data:\n')
        self.f.write('Load the following error terms data:\n')
        for i in self.ERROR_term:
            print(i)
            self.f.write(i)
            self.f.write('\n')
        self.f.close()
        self.f.close()
    
    def CHI_for_error(self):
        train_data = self.readcsv(self.ERROR_term[0])
        val_data = self.readcsv(self.ERROR_term[1])
        output = scipy.stats.chisquare(val_data, train_data)
        print('The p-value of Chi-Squared Test for error terms is ' + str(output.pvalue) + '\n')
        self.f = open(self.log_file_name,'a')
        self.f.write('The p-value of Chi-Squared Test for error terms is ' + str(output.pvalue) + '\n')
        self.f.close()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def generate_log_file(self):
        string = time.strftime('%b_%d_%Y_%H_%M_%S',time.localtime(time.time()))
        self.log_file_name = 'log_data_' + string + '.txt'
        self.f = open(self.log_file_name, 'w')
        self.f.close()  
        #self.save_folder = QFileDialog.getExistingDirectory(self,
                                                            #"Open folder",
                                                            #"./")

    ## open the data folder which contains all the data files that need to be compared, self.compared_data is a list contains the path of the file
    def open_compared_file(self):
        self.compared_data, self.compared_data_type = QFileDialog.getOpenFileNames(self,
                                                                                   "Choose data",
                                                                                   "./",
                                                                                   "CSV Files (*.csv)")  ## open file, set file type filter
        self.f = open(self.log_file_name,'a')
        print('Load the following data files for compare:')
        self.f.write('Load the following data files for compare:')
        self.f.write('\n')
        for i in self.compared_data:
            print(i)
            self.f.write(i)
            self.f.write('\n')
        self.f.close()

    ##open the two data files for test
    def open_file(self):
        self.test_data, self.test_data_type = QFileDialog.getOpenFileNames(self,
                                                                           "Choose data",
                                                                           "./",
                                                                           "CSV Files (*.CSV);;CSV Files (*.csv)")  ## open file, set file type filter
        self.f = open(self.log_file_name,'a')
        print('Load the following data files for test:\n')
        self.f.write('Load the following data files for test:\n')
        for i in self.test_data:
            print(i)
            self.f.write(i)
            self.f.write('\n')
        self.f.close()

    def cdf(self):
        for i in self.compared_data:
            print(str(type(i)))
            data = self.readcsv(i)
            num_bins = int(np.max(data) - np.min(data))
            counts, bin_edges = np.histogram(data, bins=num_bins, normed=True)
            cdf = np.cumsum(counts)
            plt.plot(bin_edges[1:], cdf / cdf[-1], label=i.split('/')[-1])
        plt.title("Frequency of Validated objective functions")
        plt.xlabel("Validated Objective")
        plt.ylabel("Cumulative frequency")
        plt.legend()
        plt.show()

    def ftest(self):
        train_data = self.readcsv(self.test_data[0])
        val_data = self.readcsv(self.test_data[1])
        output = scipy.stats.f_oneway(train_data, val_data)
        self.f = open(self.log_file_name,'a')
        print('The p-value of F Test is ' + str(output.pvalue) + '\n')
        self.f.write('The p-value of F-Test is ' + str(output.pvalue) + '\n')
        self.f.close()

    def chisquaredtest(self):
        train_data = self.readcsv(self.test_data[0])
        val_data = self.readcsv(self.test_data[1])
        output = scipy.stats.chisquare(val_data, train_data)
        print('The p-value of Chi-Squared Test is ' + str(output.pvalue) + '\n')
        self.f = open(self.log_file_name,'a')
        self.f.write('The p-value of Chi-Squared Test is ' + str(output.pvalue) + '\n')
        self.f.close()

    def ttest(self):
        train_data = self.readcsv(self.test_data[0])
        val_data = self.readcsv(self.test_data[1])
        output = scipy.stats.ttest_ind(train_data, val_data)
        print('The p-value of T Test is ' + str(output.pvalue) + '\n')
        self.f = open(self.log_file_name,'a')
        self.f.write('The p-value of T-Test is ' + str(output.pvalue) + '\n')
        self.f.close()

    def kwtest(self):
        files_nb = len(self.compared_data)
        model_types = []
        for i in range(files_nb):
            model_types.append(self.compared_data[i].split('/')[-1].split('.')[0])
        df = pd.DataFrame(index=model_types, columns=model_types)

        for i in range(files_nb):
            data1 = self.readcsv(self.compared_data[i])
            for j in range(i + 1, files_nb):
                data2 = self.readcsv(self.compared_data[j])
                output = scipy.stats.kruskal(data1, data2)
                df[model_types[i]][model_types[j]] = output.pvalue
        print('The pvalue of Kruskal-Wallis Test is')
        print(df.to_string())
        self.f = open(self.log_file_name,'a')
        self.f.write('The outcome of Kruskal-Wallis Test is:\n')
        self.f.write(df.to_string())
        self.f.close()

    def readcsv(self, filename):
        results = []
        with open(filename) as csvfile:
            reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)  # change contents to floats
            for row in reader:  # each row is a list
                results.append(row[0])
        a = np.array(results)
        return a


if __name__ == '__main__':
    app = QApplication(sys.argv)

    ex = LEO()
    sys.exit(app.exec_())
