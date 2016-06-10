<?php
require_once 'P2PUSauceBase.php';

class HomeTest extends P2PUSauceBase
{
    function testHomePage()
    {
        $this->open('/');
        $this->assertTitle('P2PU | Learning for everyone, by everyone, about almost anything');
        $this->login();
        $location = $this->getLocation();
        $this->assertStringEndsWith("/en/dashboard/", $location);
        $this->logout();
        $location = $this->getLocation();
        $this->assertStringEndsWith("/en/", $location);
    }
}
?>
