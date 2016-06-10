<?php
require_once 'PHPUnit/Extensions/SeleniumTestCase/SauceOnDemandTestCase.php';

class P2PUSauceBase extends PHPUnit_Extensions_SeleniumTestCase_SauceOnDemandTestCase
{
    const BROWSER_BASE_URL = 'alpha.p2pu.org';

    const BROWSER_AUTH_USER = '';
    const BROWSER_AUTH_PASSWORD = '';

    const TIMEOUT = 90000;

    function setUp()
    {
        /*
         * Variables potentially exposed through bootstrap
         * files passed in by Ant build target.
         */
        global $sauceOS;
        global $sauceBrowser;
        global $sauceBrowserVersion;
        
        if (empty($sauceOS))
        {
            $sauceOS = 'Windows 2003';
        }
        
        if (empty($sauceBrowser))
        {
            $sauceBrowser = 'firefox';
        }
        
        if (empty($sauceBrowserVersion))
        {
            $sauceBrowserVersion = '3.6';
        }
        
        $className = get_class($this);
        $testName = $this->getName();
        echo "\nSauce: {$className}->{$testName} ({$sauceBrowser} {$sauceBrowserVersion} on {$sauceOS})\n";
        
        /*
         * If Sauce details in environment vars then use those...
         */
        $sauceUserName = getenv('SAUCE_USER_NAME');
        $sauceAccessKey = getenv('SAUCE_ACCESS_KEY');

        /*
         * ...otherwise use the shared account.
         */
        if (empty($sauceUserName))
        {
            die("You need to set up env variable SAUCE_USER_NAME");
        }

        if (empty($sauceAccessKey))
        {
            die("You need to set up env variable SAUCE_ACCESS_KEY");
        }

        $this->setUserName($sauceUserName);
        $this->setAccessKey($sauceAccessKey);

        $this->setOs($sauceOS);
        $this->setBrowser($sauceBrowser);
        $this->setBrowserVersion($sauceBrowserVersion);
        $this->setTimeout(self::TIMEOUT);
        
        $user = self::BROWSER_AUTH_USER;
        $browserBaseUrl = self::BROWSER_BASE_URL;

        /*
         * If Browser details in environment vars then use those...
         */
        $envBrowserBaseUrl = getenv('SAUCE_BROWSER_BASE_URL');
        if (!empty($envBrowserBaseUrl))
        {
            $browserBaseUrl = $envBrowserBaseUrl;
        }


        if (empty($user))
        {
            $this->setBrowserUrl('http://'.$browserBaseUrl);
        }
        else
        {
            $this->setBrowserUrl('http://'.self::BROWSER_AUTH_USER.':'.self::BROWSER_AUTH_PASSWORD.'@'.$browserBaseUrl);
        }
    }
    
    protected function login()
    {
        $this->open('/en/login/?next=/en/');
        $this->type("id=id_username", "user-10");
        $this->type("id=id_password", "password");
        $this->click("id=login-submit-button");
        $this->waitForPageToLoad(self::TIMEOUT);
    }
    
    protected function logout()
    {
        $this->open('/en/logout/');
    }
    
    /**
     * Wait for a specified element to be present in the page.  
     * Often useful when element is expected to be populated via an AJAX call.
     * 
     * @param $locator The Selenium locator to look for (check the Selenium docs if you don't know the options).
     * @param $allowedSeconds Maximum number of seconds to wait for element to appear (default = 15).
     */
    protected function waitForElement($locator, $allowedSeconds=15)
    {
        $i = 0;
        while (true)
        {
            $i++;
            if ($i > $allowedSeconds)
            {
                $this->fail('Could not find locator after {$allowedSeconds} seconds: '.$locator);
                return false;
            }
            
            if ($this->isElementPresent($locator))
            {
                return true;
            }
            else
            {
                sleep(1);
            }
        }
    }
    
    /**
     * Wait for all active ajax requests to complete before proceeding.
     * This method takes advantage of the fact that we have access to the JQuery object, which we can query to see how
     * many active ajax requests there are.
     *
     * @param $timeout Maximum amount of time to wait in milliseconds
     */
    protected function waitForAllAjaxRequestsToComplete($timeout=30000)
    {
        $this->waitForCondition("selenium.browserbot.getCurrentWindow().jQuery.active == 0", $timeout);
    }
}
