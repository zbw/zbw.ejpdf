# -*- coding: utf-8 -*-
# Dr. Hendrik Bunke, h.bunke@zbw.eu
# 2012-04

import os
import tempfile
from subprocess import Popen, PIPE
from zope.component import getMultiAdapter, getUtility
from zope.annotation.interfaces import IAnnotations
from persistent.dict import PersistentDict
from plone.registry.interfaces import IRegistry
from zbw.ejpdf.interfaces import ICoverSettings


class Cover(object):
    """
    """
    
    def __init__(self, context):
        self.context = context

    def generate(self):
        """
        """

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ICoverSettings)

        if settings.fop_cmd:
            fop = settings.fop
        else:
            fop  = 'fop'
        fop_conf = settings.fop_conf
        
        xml_view = getMultiAdapter((self.context, self.context.REQUEST),
                name="cover_xml")
        xsl_view = getMultiAdapter((self.context, self.context.REQUEST),
                name="cover_xsl")
        fo_view = getMultiAdapter((self.context, self.context.REQUEST),
                name="cover_fo")
        xml = xml_view()
        xsl = xsl_view()
        fo = fo_view()
        xmltemp = tempfile.mktemp(suffix='.xml')
        xsltemp = tempfile.mktemp(suffix='.xsl')
        fotemp = tempfile.mktemp(suffix='.fo')
        
        self.__tmpwrite(xmltemp, xml)
        self.__tmpwrite(xsltemp, xsl)
        self.__tmpwrite(fotemp, fo)
        
        pdfname = "cover.%s.%s.pdf" %(self.context.portal_type,
                self.context.getId())

        #fop_cmd = "%s -c '%s' -xml '%s' -xsl '%s' '%s/%s'" %(fop, fop_conf,
        #            xmltemp, xsltemp, settings.pdf_dir, pdfname)


        fop_cmd = "%s -c '%s' %s '%s/%s'" %(fop, fop_conf, fotemp,
                    settings.pdf_dir, pdfname)
        
        stdin = open('/dev/null')
        stdout = stderr = PIPE

        p_fop = Popen(fop_cmd, stderr=stderr, stdout=stdout, stdin=stdin,
            shell=True)
        status_fop = p_fop.wait()
        
        if status_fop != 0:
            fop_msg = p_fop.stderr.read()
            raise FOPError(fop_msg)

        request = self.context.REQUEST
        os.unlink(xmltemp)
        os.unlink(xsltemp)
        os.unlink(fotemp)


    def __tmpwrite(self, dat, content):
        """
        writes content to file
        """
        f = open(dat, 'w')
        c = content.encode('utf-8')
        f.write(c)
        f.close()


class CoverAnnotation(object):
    """
    store form values as annotation on object
    """

    def __init__(self, context):

        self.context = context
        self.request = self.context.REQUEST
        ann = IAnnotations(self.context)
        KEY="zbw.coverdata"
        
        # for debugging and testing: first delete previously stored annotations
        del ann[KEY]

        if not ann.has_key(KEY):
            ann[KEY] = PersistentDict()
        self.ann = ann[KEY]

                
        
        # a little complicated here, but we need to combine several field
        # values from the control form, in order to get all necessary author
        # information
        #XXX could be done better, most probably ;-)
        authors = zip(self.request['author_name'], self.request['affil'],
                self.request['author_email'])
        authors_new = []
        for author in authors:
            if author[0] == self.request['corresponding_author']:
                author_new = dict(
                        name = author[0],
                        affil = author[1],
                        corresponding = True,
                        email = author[2]
                        )
            else:
                author_new = dict(
                        name = author[0],
                        affil = author[1],
                        corresponding = False,
                        email = authors[2]
                        )
            authors_new.append(author_new)
        
       
        self.ann['authors'] = authors_new
        
        keys = ["keywords", 
                "correspondence",
                "additional",
                ]

        for key in keys:
            if key in self.request:
                self.ann[key] = self.request[key]
            else:
                self.ann[key] = u""









class FOPError(Exception):
    pass

   









        

        


    


